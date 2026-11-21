from monitorcontrol import get_monitors

listMonitors = []
listMonitors2 = []

for monitor in get_monitors():
    with monitor:
        caps = monitor.get_vcp_capabilities()
        if "model" in caps:
            print(f"{caps["model"]}", "TEST PASSED") # just means found, wanted to write it as "test passed" though
            listMonitors.append(caps["model"])
            listMonitors2.append(caps.get("model", "").lower())

print("Found", len(listMonitors), "monitors with names: ", listMonitors)

print("\n" * 4 ,"If used, the names you will use and replace (omen x 25f) in ambientLight.py with, are following:  ", listMonitors2)