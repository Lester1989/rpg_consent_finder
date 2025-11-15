import pathlib
import xml.etree.ElementTree as ET
import json
import colorama

last_coverage:dict[str,float] = json.loads(pathlib.Path("last_coverage.json").read_text(encoding="utf8"))
coverage = pathlib.Path("coverage.xml").read_text(encoding="utf8")

# parse xml to get the coverage
root = ET.fromstring(coverage)
packages = root.findall(".//package")

this_coverage = {}

for package in packages:
    package_name = package.get("name")
    old_coverage = last_coverage.get(package_name,0)
    new_coverage = float(package.get("line-rate"))
    this_coverage[package_name] = new_coverage
    is_improved = new_coverage > old_coverage
    line_color = colorama.Fore.GREEN if is_improved else colorama.Fore.RED
    if new_coverage == old_coverage:
        line_color = colorama.Fore.YELLOW if new_coverage < .5 else colorama.Fore.LIGHTWHITE_EX
    print(
        line_color,
        package_name.ljust(40, "-"),
        str(new_coverage).ljust(6),
        f'({old_coverage:.2f})'.ljust(10),
        f'{"+" if is_improved else "-"}{new_coverage - old_coverage:.2f}'
    )
    classes = package.findall(".//class")
    for class_ in classes:
        class_name = class_.get("name")
        old_coverage = last_coverage.get(f"{package_name}.{class_name}",0)
        new_coverage = float(class_.get("line-rate"))
        this_coverage[f"{package_name}.{class_name}"] = new_coverage
        is_improved = new_coverage > old_coverage
        line_color = colorama.Fore.GREEN if is_improved else colorama.Fore.RED
        if new_coverage == old_coverage:
            line_color = colorama.Fore.YELLOW if new_coverage < .5 else colorama.Fore.LIGHTWHITE_EX 
        print(
            line_color,
            f' - {class_name}'.ljust(40),
            str(new_coverage).ljust(6),
            f'({old_coverage:.2f})'.ljust(10),
            f'{"+" if is_improved else "-"}{new_coverage - old_coverage:.2f}'
        )

print(colorama.Fore.RESET)
pathlib.Path("last_coverage.json").write_text(json.dumps(this_coverage,indent=4),encoding="utf8")