import re


class Person:
    id = 0
    def __init__(self, gen: int, name: str, desc: str, parent):
        self.id: int = Person.id
        Person.id += 1
        self.gen: int = gen
        self.name: str = name
        self.desc: str = desc
        self.parent: Person = parent
        self.children: list[Person] = []


def parse_name(s: str) -> str:
    seperator_idx = s.find(":")
    last_space_idx = s[0:seperator_idx].rfind(" ")
    return s[0:last_space_idx]

last_seen: list[Person] = []
for i in range(20):
    last_seen.append(None)

last_seen[0] = Person(0, "ROOT", "ROOT", None)

with open("res/wallicks.txt", encoding="utf8") as file:
    for line in file:
        parsed = re.search("(\.*)([0-9]*) (.*)", line)

        gen = parsed.group(2)
        if gen is None or gen == "":
            continue

        gen = int(gen)
        name = parse_name(parsed.group(3))

        parent = last_seen[gen-1]
        me = Person(gen, name, "", parent)
        parent.children.append(me)
        last_seen[gen] = me

dot: str = "digraph G {\n"
kerby: Person = None
def append_to_dot(p: Person):
    global dot
    global kerby
    if p.name.startswith("Kerby"):
        kerby = p
    # dot += str(p.id) + " [label=\"" + str(p.gen) + ". " + p.name.replace("\"", "\\\"") + "\"]\n"
    for c in p.children:
        # dot += str(p.id) + " -> " + str(c.id) + "\n"
        append_to_dot(c)

append_to_dot(last_seen[0])

curr: Person = kerby
while curr is not None:
    dot += str(curr.id) + " [label=\"" + str(curr.gen) + ". " + curr.name.replace("\"", "\\\"") + "\" color=\"blue\"]\n"
    for c in curr.children:
        dot += str(c.id) + " [label=\"" + str(c.gen) + ". " + c.name.replace("\"", "\\\"") + "\"]\n"
        dot += str(curr.id) + " -> " + str(c.id) + "\n"
    print(curr.gen, curr.name)
    curr = curr.parent


dot += "}"

with open('res/wallicks.dot', 'w') as file:
    file.write(dot)
