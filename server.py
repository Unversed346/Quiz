#!/usr/bin/env python3
import asyncio
import json
import os
import random
from pathlib import Path
from urllib.parse import urlparse

import websockets
from websockets.exceptions import ConnectionClosed
from websockets.datastructures import Headers
from websockets.http11 import Response

PORT = int(os.getenv("PORT", "3000"))
BASE_DIR = Path(__file__).resolve().parent

STATIC_FILES = {
    "/": "index.html",
    "/index.html": "index.html",
    "/host.html": "host.html",
    "/player.html": "player.html",
}

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
}

questions = [
    {
        "text": "What is the ideal temperature for grilling steak?",
        "answers": ["350°F (175°C)", "450°F (230°C)", "250°F (120°C)", "500°F (260°C)"],
        "correct": 1,
    },
    {
        "text": "How long should you let a steak rest after grilling?",
        "answers": ["1 minute", "5 minutes", "15 minutes", "30 minutes"],
        "correct": 1,
    },
    {
        "text": "What should you do to meat before applying dry rub?",
        "answers": ["Wash it", "Pat it dry", "Freeze it", "Boil it"],
        "correct": 1,
    },
    {
        "text": "Which wood is NOT good for smoking BBQ?",
        "answers": ["Apple wood", "Oak", "Pine", "Mesquite"],
        "correct": 2,
    },
    {
        "text": "What is the 'stall' in BBQ?",
        "answers": ["When grill runs out of gas", "When meat stops temp rising", "When party ends", "When coals die"],
        "correct": 1,
    },
]


class Game:
    def __init__(self, code):
        self.code = code
        self.players = {}
        self.host = None
        self.current_question = -1
        self.answer_open = False
        self.scores = {}
        self.submissions = set()
        self.time_limit = 20
        self.timer_task = None


games = {}


def generate_code():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(random.choice(chars) for _ in range(6))


def player_list(game):
    return [{"name": player["name"], "score": player["score"]} for player in game.players.values()]


async def send_answer_count(game):
    await safe_send(
        game.host,
        json.dumps(
            {
                "type": "answer-count",
                "count": len(game.submissions),
                "totalPlayers": len(game.players),
            }
        ),
    )


async def safe_send(websocket, payload):
    if websocket is None:
        return

    try:
        await websocket.send(payload)
    except Exception:
        pass


async def broadcast_to_players(game, payload):
    for player in list(game.players.values()):
        await safe_send(player["websocket"], payload)


def http_response(status_code, reason_phrase, body, content_type):
    headers = Headers()
    headers["Content-Type"] = content_type
    headers["Content-Length"] = str(len(body))
    headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return Response(status_code, reason_phrase, headers, body)


def load_static_response(path):
    filename = STATIC_FILES.get(path)
    if filename is None:
        body = b"Not Found"
        return http_response(404, "Not Found", body, "text/plain; charset=utf-8")

    file_path = BASE_DIR / filename
    if not file_path.exists():
        body = b"Missing file"
        return http_response(500, "Internal Server Error", body, "text/plain; charset=utf-8")

    body = file_path.read_bytes()
    content_type = CONTENT_TYPES.get(file_path.suffix, "application/octet-stream")
    return http_response(200, "OK", body, content_type)


async def process_request(connection, request):
    path = urlparse(request.path).path
    if path == "/ws":
        return None
    return load_static_response(path)


async def handle_client(websocket):
    client_id = id(websocket)

    try:
        async for message in websocket:
            if not message:
                continue

            data = message.split(":")
            cmd = data[0]

            if cmd == "host":
                code = data[1] if len(data) > 1 and data[1] else generate_code()
                game = games.get(code)

                if game is None:
                    game = Game(code)
                    games[code] = game

                game.host = websocket
                await safe_send(websocket, json.dumps({"type": "lobby-created", "lobbyCode": code}))

            elif cmd == "join":
                code = data[1] if len(data) > 1 else ""
                name = ":".join(data[2:]) if len(data) > 2 else "Guest"

                if code not in games:
                    await safe_send(websocket, json.dumps({"type": "error", "message": "Game not found"}))
                    continue

                game = games[code]
                game.players[client_id] = {"websocket": websocket, "name": name, "score": 0}
                game.scores[client_id] = 0

                await safe_send(websocket, json.dumps({"type": "joined", "name": name}))
                await safe_send(game.host, json.dumps({"type": "player-joined", "players": player_list(game)}))

            elif cmd == "host-start":
                code = data[1] if len(data) > 1 else ""
                game = games.get(code)
                if game is None:
                    continue

                game.current_question = -1
                await next_question(game)

            elif cmd == "host-next":
                code = data[1] if len(data) > 1 else ""
                game = games.get(code)
                if game is None:
                    continue

                if game.current_question < len(questions) - 1:
                    await next_question(game)
                else:
                    await end_game(game)

            elif cmd == "answer":
                code = data[1] if len(data) > 1 else ""
                answer_idx = int(data[2]) if len(data) > 2 else 0
                game = games.get(code)

                if game is None or not game.answer_open or client_id not in game.players:
                    continue

                if client_id in game.submissions:
                    continue

                is_correct = 1 if answer_idx == questions[game.current_question]["correct"] else 0
                points = is_correct * 1000
                game.submissions.add(client_id)
                game.scores[client_id] = game.scores.get(client_id, 0) + points
                game.players[client_id]["score"] = game.scores[client_id]

                await safe_send(
                    websocket,
                    json.dumps({"type": "answer-result", "correct": is_correct, "points": points}),
                )
                await send_answer_count(game)

                if game.players and len(game.submissions) >= len(game.players):
                    await finish_question(game)
    except ConnectionClosed:
        pass

    finally:
        for code, game in list(games.items()):
            if game.host == websocket:
                game.host = None
            elif client_id in game.players:
                del game.players[client_id]
                del game.scores[client_id]
                await safe_send(game.host, json.dumps({"type": "player-left", "players": player_list(game)}))
                if game.answer_open:
                    await send_answer_count(game)

            if game.host is None and not game.players:
                if game.timer_task is not None:
                    game.timer_task.cancel()
                del games[code]


async def next_question(game):
    if game.timer_task is not None:
        game.timer_task.cancel()
        game.timer_task = None

    game.current_question += 1
    game.answer_open = True
    game.submissions = set()

    question = questions[game.current_question]
    payload = json.dumps(
        {
            "type": "question",
            "number": game.current_question + 1,
            "total": len(questions),
            "text": question["text"],
            "answers": question["answers"],
            "timeLimit": game.time_limit,
        }
    )

    await safe_send(game.host, payload)
    await broadcast_to_players(game, payload)
    await send_answer_count(game)
    game.timer_task = asyncio.create_task(question_timer(game, question["correct"]))


async def question_timer(game, correct_index):
    try:
        await asyncio.sleep(game.time_limit)
        await finish_question(game, correct_index)
    except asyncio.CancelledError:
        pass


async def finish_question(game, correct_index=None):
    if not game.answer_open:
        return

    game.answer_open = False
    if game.timer_task is not None:
        game.timer_task.cancel()
        game.timer_task = None

    if correct_index is None and game.current_question >= 0:
        correct_index = questions[game.current_question]["correct"]

    time_up_payload = json.dumps({"type": "time-up", "correct": correct_index})
    await safe_send(game.host, time_up_payload)
    await broadcast_to_players(game, time_up_payload)


async def end_game(game):
    leaderboard = sorted(player_list(game), key=lambda player: player["score"], reverse=True)[:10]
    payload = json.dumps({"type": "game-over", "leaderboard": leaderboard})
    await safe_send(game.host, payload)
    await broadcast_to_players(game, payload)


async def main():
    async with websockets.serve(handle_client, "0.0.0.0", PORT, process_request=process_request):
        print(f"BBQ Quiz running on http://0.0.0.0:{PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
