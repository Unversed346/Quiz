#!/usr/bin/env python3
import asyncio
import json
import os
import random
from pathlib import Path

from aiohttp import WSMsgType, web

PORT = int(os.getenv("PORT", "3000"))
BASE_DIR = Path(__file__).resolve().parent

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
    {
        "text": "Which cut is most commonly used for pulled pork?",
        "answers": ["Pork belly", "Pork loin", "Pork shoulder", "Pork chop"],
        "correct": 2,
    },
    {
        "text": "Which of these is a 'low and slow' cooking temperature?",
        "answers": ["225°F (107°C)", "375°F (190°C)", "450°F (230°C)", "525°F (274°C)"],
        "correct": 0,
    },
    {
        "text": "What does 'direct heat' mean on a grill?",
        "answers": ["Food cooks beside the flame", "Food cooks over the heat source", "Food cooks in foil", "Food cooks after resting"],
        "correct": 1,
    },
    {
        "text": "What is the main benefit of letting chicken marinade sit for a few hours?",
        "answers": ["It cools the meat", "It adds flavor", "It removes fat", "It fully cooks it"],
        "correct": 1,
    },
    {
        "text": "Which wood gives a mild, slightly sweet smoke flavor?",
        "answers": ["Apple", "Hickory", "Oak", "Pine"],
        "correct": 0,
    },
    {
        "text": "What should you use to check if meat is safely cooked?",
        "answers": ["A fork", "A timer only", "A meat thermometer", "The smoke color"],
        "correct": 2,
    },
    {
        "text": "Which of these burgers is safest to cook to well done?",
        "answers": ["Ground beef burger", "Steak", "Lamb chop", "Pork tenderloin"],
        "correct": 0,
    },
    {
        "text": "Why do people oil the grill grates before cooking?",
        "answers": ["To cool them down", "To stop food sticking", "To make more smoke", "To season the salad"],
        "correct": 1,
    },
    {
        "text": "What color should chicken juices run when properly cooked?",
        "answers": ["Pink", "Red", "Clear", "Green"],
        "correct": 2,
    },
    {
        "text": "What is a common sign that charcoal is ready for cooking?",
        "answers": ["It is dripping", "It turns grey-white", "It goes completely black", "It stops being hot"],
        "correct": 1,
    },
    {
        "text": "Which sauce is most associated with Kansas City BBQ?",
        "answers": ["Thin vinegar sauce", "White mayo sauce", "Thick sweet tomato sauce", "No sauce at all"],
        "correct": 2,
    },
    {
        "text": "What is the purpose of resting brisket after cooking?",
        "answers": ["To make it colder", "To let juices redistribute", "To add more smoke", "To crisp the bark"],
        "correct": 1,
    },
    {
        "text": "What is the danger of pressing burgers with a spatula while cooking?",
        "answers": ["It adds too much salt", "It squeezes out juices", "It makes them cook faster", "It removes grill marks"],
        "correct": 1,
    },
    {
        "text": "Which BBQ region is famous for white sauce with chicken?",
        "answers": ["Texas", "Alabama", "Kansas", "Memphis"],
        "correct": 1,
    },
    {
        "text": "Which of these foods is usually cooked with indirect heat?",
        "answers": ["A whole chicken", "Thin burger patties", "Hot dogs", "Shrimp skewers"],
        "correct": 0,
    },
    {
        "text": "What does 'searing' do best?",
        "answers": ["Adds a browned crust", "Fully cooks the center", "Reduces smoke", "Makes meat sweeter"],
        "correct": 0,
    },
    {
        "text": "Which ingredient is most common in a dry rub?",
        "answers": ["Powdered sugar", "Paprika", "Mayonnaise", "Soy milk"],
        "correct": 1,
    },
    {
        "text": "What is the safest way to thaw meat before a BBQ?",
        "answers": ["On the counter all day", "In the fridge", "In direct sunlight", "Next to the grill"],
        "correct": 1,
    },
    {
        "text": "What kind of ribs come from the upper rib cage near the backbone?",
        "answers": ["Spare ribs", "Baby back ribs", "Short ribs", "Country-style ribs"],
        "correct": 1,
    },
    {
        "text": "If flames flare up under fatty meat, what should you do first?",
        "answers": ["Spray lots of water", "Move the meat to cooler heat", "Close your eyes", "Add more oil"],
        "correct": 1,
    },
    {
        "text": "Which cut is the classic choice for beef brisket BBQ?",
        "answers": ["Tenderloin", "Brisket", "Sirloin", "Flank"],
        "correct": 1,
    },
    {
        "text": "What is the main fuel source in a pellet grill?",
        "answers": ["Wood pellets", "Charcoal briquettes", "Natural gas", "Sterno cans"],
        "correct": 0,
    },
    {
        "text": "What is a common internal temperature target for pulled pork?",
        "answers": ["145°F (63°C)", "165°F (74°C)", "180°F (82°C)", "203°F (95°C)"],
        "correct": 3,
    },
    {
        "text": "What is the 'bark' on smoked meat?",
        "answers": ["The bone", "The dark outer crust", "A sauce layer", "The fat cap"],
        "correct": 1,
    },
    {
        "text": "Which BBQ style is most associated with vinegar-based pork sauce?",
        "answers": ["Eastern North Carolina", "Kansas City", "Alabama white sauce", "Santa Maria"],
        "correct": 0,
    },
    {
        "text": "Why use a two-zone fire on a grill?",
        "answers": ["To cook with only smoke", "To have hot and cooler areas", "To save charcoal forever", "To stop all flare-ups"],
        "correct": 1,
    },
    {
        "text": "Which steak is known for heavy marbling and rich flavor?",
        "answers": ["Ribeye", "Round steak", "Eye of round", "Cube steak"],
        "correct": 0,
    },
    {
        "text": "What should you do with wooden skewers before grilling?",
        "answers": ["Freeze them", "Soak them in water", "Paint them with oil", "Break them shorter"],
        "correct": 1,
    },
    {
        "text": "What is the safest minimum internal temperature for cooked chicken?",
        "answers": ["145°F (63°C)", "155°F (68°C)", "165°F (74°C)", "185°F (85°C)"],
        "correct": 2,
    },
    {
        "text": "Which grill setup is best for smoking ribs low and slow?",
        "answers": ["Direct flame on high", "Indirect heat", "Open flame with lid off", "Cast iron on the hob"],
        "correct": 1,
    },
    {
        "text": "What is mop sauce usually used for during smoking?",
        "answers": ["Basting meat during cooking", "Cleaning the grill", "Cooling charcoal", "Thickening bark only"],
        "correct": 0,
    },
    {
        "text": "Which meat is most associated with Santa Maria barbecue?",
        "answers": ["Tri-tip", "Pork shoulder", "Whole hog", "Turkey legs"],
        "correct": 0,
    },
    {
        "text": "What is one sign your grill is too crowded?",
        "answers": ["Food browns quickly", "Heat cannot circulate well", "There are too many grill marks", "The lid closes easily"],
        "correct": 1,
    },
    {
        "text": "What is the main reason to keep the lid closed during smoking?",
        "answers": ["To keep heat and smoke steady", "To make the grill lighter", "To reduce seasoning", "To stop meat resting"],
        "correct": 0,
    },
    {
        "text": "What is a common ingredient in Alabama white sauce?",
        "answers": ["Mayonnaise", "Soy sauce", "Maple syrup", "Coconut milk"],
        "correct": 0,
    },
    {
        "text": "When cooking sausages, what helps prevent burnt outsides and raw middles?",
        "answers": ["Cooking only over the hottest flame", "Using gentler heat", "Piercing them repeatedly", "Rolling them in sugar"],
        "correct": 1,
    },
    {
        "text": "What is the best reason to preheat a grill?",
        "answers": ["It makes meat colder", "It helps prevent sticking and cooks evenly", "It removes smoke flavor", "It cuts cooking time to zero"],
        "correct": 1,
    },
    {
        "text": "Which BBQ meat is commonly wrapped during the stall to push through it?",
        "answers": ["Brisket", "Hot dogs", "Chicken wings", "Burgers"],
        "correct": 0,
    },
    {
        "text": "What does 'carryover cooking' mean?",
        "answers": ["Food keeps cooking after being removed from heat", "Food cooks while carried to the table", "Meat cools faster after grilling", "Sauce burns after serving"],
        "correct": 0,
    },
    {
        "text": "Why should raw meat and cooked meat use separate plates?",
        "answers": ["To look nicer", "To avoid cross-contamination", "To save washing up", "To hold more sauce"],
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
        self.active_questions = random.sample(questions, k=min(len(questions), 40))


games = {}


def generate_code():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(random.choice(chars) for _ in range(6))


def player_list(game):
    return [{"name": player["name"], "score": player["score"]} for player in game.players.values()]


async def safe_send(socket, payload):
    if socket is None or socket.closed:
        return

    try:
        await socket.send_str(payload)
    except Exception:
        pass


async def broadcast_to_players(game, payload):
    for player in list(game.players.values()):
        await safe_send(player["socket"], payload)


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


async def finish_question(game, correct_index=None):
    if not game.answer_open:
        return

    game.answer_open = False
    if game.timer_task is not None:
        game.timer_task.cancel()
        game.timer_task = None

    if correct_index is None and game.current_question >= 0:
        correct_index = game.active_questions[game.current_question]["correct"]

    payload = json.dumps({"type": "time-up", "correct": correct_index})
    await safe_send(game.host, payload)
    await broadcast_to_players(game, payload)


async def question_timer(game, correct_index):
    try:
        await asyncio.sleep(game.time_limit)
        await finish_question(game, correct_index)
    except asyncio.CancelledError:
        pass


async def next_question(game):
    if game.timer_task is not None:
        game.timer_task.cancel()
        game.timer_task = None

    game.current_question += 1
    game.answer_open = True
    game.submissions = set()

    question = game.active_questions[game.current_question]
    is_double = (game.current_question + 1) % 3 == 0
    payload = json.dumps(
        {
            "type": "question",
            "number": game.current_question + 1,
            "total": len(game.active_questions),
            "text": question["text"],
            "answers": question["answers"],
            "timeLimit": game.time_limit,
            "doublePoints": is_double,
        }
    )

    await safe_send(game.host, payload)
    await broadcast_to_players(game, payload)
    await send_answer_count(game)
    game.timer_task = asyncio.create_task(question_timer(game, question["correct"]))


async def end_game(game):
    leaderboard = sorted(player_list(game), key=lambda player: player["score"], reverse=True)[:10]
    payload = json.dumps({"type": "game-over", "leaderboard": leaderboard})
    await safe_send(game.host, payload)
    await broadcast_to_players(game, payload)


async def cleanup_socket(socket):
    client_id = id(socket)

    for code, game in list(games.items()):
        if game.host == socket:
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


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    client_id = id(ws)

    try:
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                continue

            message = msg.data
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

                game.host = ws
                await safe_send(ws, json.dumps({"type": "lobby-created", "lobbyCode": code}))

            elif cmd == "join":
                code = data[1] if len(data) > 1 else ""
                name = ":".join(data[2:]) if len(data) > 2 else "Guest"

                if code not in games:
                    await safe_send(ws, json.dumps({"type": "error", "message": "Game not found"}))
                    continue

                game = games[code]
                game.players[client_id] = {"socket": ws, "name": name, "score": 0}
                game.scores[client_id] = game.scores.get(client_id, 0)
                game.players[client_id]["score"] = game.scores[client_id]

                await safe_send(ws, json.dumps({"type": "joined", "name": name}))
                await safe_send(game.host, json.dumps({"type": "player-joined", "players": player_list(game)}))
                if game.answer_open:
                    await send_answer_count(game)

            elif cmd == "host-start":
                code = data[1] if len(data) > 1 else ""
                game = games.get(code)
                if game is None:
                    continue

                game.current_question = -1
                game.active_questions = random.sample(questions, k=min(len(questions), 40))
                await next_question(game)

            elif cmd == "host-next":
                code = data[1] if len(data) > 1 else ""
                game = games.get(code)
                if game is None:
                    continue

                if game.current_question < len(game.active_questions) - 1:
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

                current_question = game.active_questions[game.current_question]
                is_correct = 1 if answer_idx == current_question["correct"] else 0
                multiplier = 2 if (game.current_question + 1) % 3 == 0 else 1
                points = is_correct * 1000 * multiplier
                game.submissions.add(client_id)
                game.scores[client_id] = game.scores.get(client_id, 0) + points
                game.players[client_id]["score"] = game.scores[client_id]

                await safe_send(
                    ws,
                    json.dumps({"type": "answer-result", "correct": is_correct, "points": points}),
                )
                await send_answer_count(game)

                if game.players and len(game.submissions) >= len(game.players):
                    await finish_question(game)

    finally:
        await cleanup_socket(ws)

    return ws


async def file_handler(request):
    requested = request.match_info["filename"]
    allowed = {"index.html", "host.html", "player.html"}
    if requested not in allowed:
        raise web.HTTPNotFound(text="Not Found")
    return web.FileResponse(BASE_DIR / requested, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})


async def root_handler(request):
    return web.FileResponse(BASE_DIR / "index.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"})


def make_app():
    app = web.Application()
    app.router.add_get("/", root_handler)
    app.router.add_get("/ws", websocket_handler)
    app.router.add_get(r"/{filename:index\.html|host\.html|player\.html}", file_handler)
    return app


if __name__ == "__main__":
    print(f"BBQ Quiz running on http://0.0.0.0:{PORT}")
    web.run_app(make_app(), host="0.0.0.0", port=PORT)
