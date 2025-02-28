# to remove the version number and dup after pulled all reqs using pipreqs
unique_req = set()
with open('requirements.txt', 'r') as infile, open('cleaned_requirements.txt', 'w') as output:
    for line in infile:
        package = line.split('==')[0].strip()
        unique_req.add(package)

    for package in unique_req:
        output.write(package + "\n")
    print(f"Done cleaning")