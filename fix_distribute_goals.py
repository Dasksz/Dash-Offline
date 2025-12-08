import re

file_path = 'EXPORTADOR DASH V7.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Target function signature
start_marker = "function distributePositivacao() {"
# End marker (a distinct line after the function body)
# In previous implementation, the function ended with updateGoalsView(); }
end_marker = "updateGoalsView();"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx != -1 and end_idx != -1:
    brace_idx = content.find("}", end_idx)
    if brace_idx != -1:
        # The replacement function code
        new_function = r"""function distributePositivacao() {
            if (selectedGoalsGvSellers.length !== 1) {
                alert("Selecione apenas um vendedor para definir a meta de positivação.");
                return;
            }

            const sellerName = selectedGoalsGvSellers[0];
            const inputVal = parseInputMoney('goal-global-mix');

            // INDEPENDENT LOGIC: Only update the specific target key. No propagation.

            if (!globalSellerGoals[sellerName]) globalSellerGoals[sellerName] = {};

            const currentKey = currentGoalsSupplier + (currentGoalsBrand ? '_' + currentGoalsBrand : '');

            if (!globalSellerGoals[sellerName][currentKey]) globalSellerGoals[sellerName][currentKey] = { pos: 0 };
            globalSellerGoals[sellerName][currentKey].pos = inputVal;

            updateGoalsView();
        }"""

        new_content = content[:start_idx] + new_function + content[brace_idx+1:]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully patched 'distributePositivacao'")
    else:
        print("Could not find closing brace for the function.")
else:
    print("Could not find the start or end of the target function.")
