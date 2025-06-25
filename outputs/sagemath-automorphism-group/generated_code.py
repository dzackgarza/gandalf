# GroupInput module
from sage.groups.perm_gps import PermutationGroup
from sage.groups.group import Group

class InputParser:
    def parse(self, input_string):
        """Parses various group representations into a SageMath group object."""
        try:
            # Attempt to parse as a permutation group string
            return PermutationGroup(input_string)
        except:
            try:
                # Attempt to parse as a group presentation (if needed, add more sophisticated parsing)
                # ...  (Add more robust presentation parsing here if required) ...
                raise ValueError("Presentation parsing not yet implemented.")
            except:
                raise ValueError("Invalid group representation.")


class GroupValidator:
    def validate(self, group):
        """Checks if input is a valid finite group."""
        if not isinstance(group, Group):
            raise ValueError("Input is not a SageMath group object.")
        if group.order() == float('inf'):
            raise ValueError("Input group is not finite.")
        return True


# AutomorphismComputation module
from sage.groups.perm_gps import AutomorphismGroup

class AutomorphismAlgorithm:
    def compute(self, group):
        """Computes the automorphism group using Sage's built-in functionality."""
        try:
            return AutomorphismGroup(group)
        except Exception as e:
            raise RuntimeError(f"Error computing automorphism group: {e}")


# OutputFormatter module
class PermutationGroupOutput:
    def format(self, automorphism_group):
        """Formats the automorphism group as a permutation group and presents it in a readable format."""
        return automorphism_group


#Main Script
from GroupInput import InputParser, GroupValidator
from AutomorphismComputation import AutomorphismAlgorithm
from OutputFormatter import PermutationGroupOutput

def compute_automorphism_group(group_representation):
    """Main function to compute the automorphism group."""
    parser = InputParser()
    validator = GroupValidator()
    algorithm = AutomorphismAlgorithm()
    formatter = PermutationGroupOutput()

    try:
        group = parser.parse(group_representation)
        if validator.validate(group):
            automorphism_group = algorithm.compute(group)
            formatted_output = formatter.format(automorphism_group)
            return formatted_output
        else:
            return "Invalid group input."
    except ValueError as e:
        return f"Error: {e}"
    except RuntimeError as e:
        return f"Error: {e}"


# Example usage and testing:
groups_to_test = [
    "SymmetricGroup(3)",
    "DihedralGroup(5)",
    "CyclicPermutationGroup(7)",
    "(a,b | a^2=b^3=(ab)^7=1)", #Example presentation (requires implementation in InputParser)
    "S5",
    "1", #trivial group
]


for group_rep in groups_to_test:
    print(f"Computing automorphism group for: {group_rep}")
    result = compute_automorphism_group(group_rep)
    print(result)
    print("-" * 20)
