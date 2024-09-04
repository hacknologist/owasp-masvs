import os
import yaml
import re
import argparse

masvs = {
    "metadata": {
        "title": "Mobile Application Security Verification Standard (MASVS)",
        "remarks": "The OWASP MASVS (Mobile Application Security Verification Standard) is the industry standard for mobile app security. It can be used by mobile software architects and developers seeking to develop secure mobile apps, as well as security testers to ensure completeness and consistency of test results."
    },
    "groups": []
}

def read_md_sections(input_text):

    sections_dict = {}

    sections = re.split(r'^##\s(.+)', input_text, flags=re.MULTILINE)
    sections.pop(0)  # Remove the initial empty string
    
    # Loop over the sections and write each one to a separate file
    for i in range(0, len(sections), 2):
        section_title = sections[i].strip()
        section_content = sections[i+1].strip()

        if section_title == "Control":
            sections_dict["statement"] = section_content
        elif section_title == "Description":
            sections_dict["description"] = section_content
    
    return sections_dict

def get_masvs_dict(masvs_version, input_dir, controls_dir):
    index = 1

    for file in sorted(os.listdir(input_dir)):
        if "-MASVS-" in file:
            with open(os.path.join(input_dir, file), "r") as f:
                header = f.readline().replace("# ", "").strip()
                description = f.read()
                category_id = header.split(":")[0].strip()
                title = header.split(":")[1].strip()
                group = {
                    "id": category_id,
                    "index": index,
                    "title": title,
                    "description": description, 
                    "controls": []
                }

                for control_file in os.listdir(controls_dir):
                    if control_file.startswith(category_id):
                        with open(os.path.join(controls_dir, control_file), "r") as cf:
                            control_id = cf.readline().replace("# ", "").strip()
                            control_content = cf.read()
                            control_sections = read_md_sections(control_content)
                            control = {"id": control_id} | control_sections
                            group["controls"].append(control)
                group["controls"] = sorted(group["controls"], key=lambda k: k["id"])
                masvs["groups"].append(group)
            index += 1
    # sort masvs dict by index
    masvs["groups"] = sorted(masvs["groups"], key=lambda k: k["index"])
    
    masvs["metadata"]["version"] = masvs_version
    return masvs

# get input arguments
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Input Directory", required=False, default="Document")
parser.add_argument("-c", "--controls", help="Controls Directory", required=False, default="controls")
parser.add_argument("-v", "--version", help="MASVS version", required=False, default="vx.x.x")
args = parser.parse_args()

masvs_version = args.version
input_dir = args.input
controls_dir = args.controls

masvs = get_masvs_dict(masvs_version, input_dir, controls_dir)

with open("OWASP_MASVS.yaml", "w") as f:
    yaml.dump(masvs, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=float("inf"))
