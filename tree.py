import re


class Person:
    id = 0
    def __init__(self, gen: int, first_name: str, middle_name:str, last_name: str):
        self.id: int = Person.id
        Person.id += 1
        self.gen: int = gen
        self.first_name: str = first_name
        self.middle_name: str = middle_name
        self.last_name: str = last_name
        self.parent: Person = None
        self.spouse: Person = None
        self.children: list[Person] = []

        self.notes: str = ""
        self.props = {}

    def from_book_line(line: str):
        parsed = re.search("^(\.*)([0-9]*) (.*)", line)
        gen = int(parsed.group(2))
        line = parsed.group(3)

        props = {}
        while line is not None and line != "":
            last_colon_idx = line.rfind(": ")
            if last_colon_idx < 0:
                break
            last_space_before_colon_idx = line[0:last_colon_idx].rfind(" ")
            key = line[last_space_before_colon_idx + 1:last_colon_idx]
            val = line[last_colon_idx + 2:]
            props[key] = val
            line = line[0:last_space_before_colon_idx]

        (first_name, middle_name, last_name) = Person.parse_names(line)
        person = Person(gen, first_name, middle_name, last_name)
        person.props = props
        return person

    def parse_names(line: str) -> tuple[str, str, str]:
        first_space_idx = line.find(" ")
        last_space_idx = line.rfind(" ")

        if first_space_idx < 0:
            return (line, None, None)
        
        if first_space_idx == last_space_idx:
            return (line[0:first_space_idx], None, line[last_space_idx + 1:])

        return (line[0:first_space_idx], line[first_space_idx + 1:last_space_idx], line[last_space_idx + 1:])


    def add_spouse(self, first_name: str, last_name: str):
        self.spouse = Person(self.gen, first_name, last_name)

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def name_str(self) -> str:
        name = self.first_name
        if self.middle_name is not None:
            name += " " + self.middle_name
        if self.last_name is not None:
            name += " " + self.last_name
        return name

    def to_dot_str(self, attrs: str = None) -> str:
        dot = str(self.id) + " [label=\"" + str(self.gen) + ". " + self.name_str().replace("\"", "\\\"") + "\" "
        if attrs is not None:
            dot += attrs
        dot += "]\n"
        return dot

def parse_book_file() -> Person:
    last_seen: list[Person] = []
    for i in range(20):
        last_seen.append(None)

    root = Person(0, "ROOT", "ROOT", "ROOT")
    last_seen[0] = root
    last: Person = None
    with open("res/wallicks_cleaned.txt", encoding="utf8") as file:
        for line in file:
            line = line.strip()

            # Spouse
            if line.startswith("+"):
                continue

            me = Person.from_book_line(line)
            last_seen[me.gen-1].add_child(me)
            last_seen[me.gen] = me
            last = me
    
    root = root.children[0]
    root.parent = None
    return root

def dot_from_top(person: Person) -> str:
    dot = person.to_dot_str()
    for child in person.children:
        dot += dot_from_top(child)
    if person.parent is not None:
        dot += str(person.parent.id) + " -> " + str(person.id) + "\n"

    return dot

def dot_from_bottom(person: Person) -> str:
    curr: Person = person
    dot = ""
    while curr is not None:
        dot += curr.to_dot_str("color=\"blue\"")
        for child in curr.children:
            dot += child.to_dot_str()
            dot += str(curr.id) + " -> " + str(child.id) + "\n"
        curr = curr.parent

    return dot


def save_dot(root: Person):
    dot = "digraph G {\n" + dot_from_top(root) + "}"
    with open('res/wallicks.dot', 'w') as file:
        file.write(dot)

def save_trimmed_dot(root: Person):
    me = find_by_name(root, "Kerby").children[0]
    dot = "digraph G {\n" + dot_from_bottom(me) + "}"
    with open('res/wallicks_trimmed.dot', 'w') as file:
        file.write(dot)

def find_by_name(root: Person, name: str):
    if root.first_name == name:
        return root

    for child in root.children:
        result = find_by_name(child, name)
        if result is not None:
            return result

    return None


def clean_book_file():
    lines = ""
    with open("res/wallicks.txt", encoding="utf8") as file:
        for line in file:
            line = line.replace("\n", "")

            # If the line starts with a number, it's a new entry
            if re.search("^(\.)*[0-9]+.*", line) is not None:
                lines += "\n" + line

            # If the line starts with a plus, it's a spouse
            elif re.search("^(\.| )*\++.*", line) is not None:
                lines += "\n" + line

            # Otherwise, it's extra description
            else:
                lines += " " + line.strip()

    # Remove leading \n
    lines = lines[1:]

    with open('res/wallicks_cleaned.txt', "w", encoding="utf8") as file:
        file.write(lines)
    

clean_book_file()
root = parse_book_file()
save_dot(root)
save_trimmed_dot(root)

# def gedcom():
#     with open('res/wallicks.ged', 'w') as file:
#         file.write(dot)


