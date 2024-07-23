import toml

# Load the TOML file
data = toml.load('pyproject.toml')

# Get the dependencies
dependencies = data['project']['dependencies']

# Write the dependencies to a requirements.txt file
with open('requirements.txt', 'w') as f:
    for dependency in dependencies:
        f.write(dependency + '\n')

# Get the dev dependencies
dev_dependencies = data['tool']['rye']['dev-dependencies']

# Expand the optional dependencies
optional_dependencies = data['project']['optional-dependencies']
expanded_dev_dependencies = []
for dependency in dev_dependencies:
    if dependency.startswith('-e file:.'):
        optional_dependency_name = dependency.split('.')[1][1:-1]
        expanded_dev_dependencies.extend(optional_dependencies[optional_dependency_name])
    else:
        expanded_dev_dependencies.append(dependency)

# Write the expanded dev dependencies to a requirements-dev.txt file
with open('requirements-dev.txt', 'w') as f:
    for dependency in expanded_dev_dependencies:
        f.write(dependency + '\n')