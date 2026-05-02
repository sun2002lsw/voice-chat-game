import winsound

from dotenv import load_dotenv

from scenario import ScenarioManager

load_dotenv()

scenario = ScenarioManager().get("카페 주문")

while True:
    output = scenario.get_output()
    print(output.script.read_text(encoding="utf-8"))
    winsound.PlaySound(str(output.voice), winsound.SND_FILENAME)

    user_input = input("> ")
    if user_input == "q":
        break

    scenario.invoke(user_input)
