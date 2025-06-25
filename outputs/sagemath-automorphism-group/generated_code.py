# automorphism_group_computation.py
from sage.all import *
import sys

class GroupInputHandler:
    """Handles input validation and group representation for automorphism computation."""

    @staticmethod
    def validate_input(group):
        """Validate that the input is a valid finite group in SageMath."""
        if not hasattr(group, 'is_finite') or not group.is_finite():
            raise ValueError("Input must be a finite group")
        if not hasattr(group, 'is_permutation_group'):
            raise ValueError("Input must be a permutation group representation")
        return True

    @staticmethod
    def standardize_representation(group):
        """Ensure the group is in a standard form for computation."""
        try:
            # Convert to permutation group if it isn't already
            if not group.is_permutation_group():
                return group.permutation_group()
            return group
        except AttributeError as e:
            raise ValueError(f"Group cannot be converted to permutation group: {str(e)}")

class AutomorphismComputer:
    """Computes the automorphism group of a given finite group."""

    @staticmethod
    def compute_automorphism_group(group):
        """Compute the automorphism group using SageMath's built-in functions."""
        try:
            # First try the direct computation
            return group.automorphism_group()
        except (NotImplementedError, AttributeError):
            # Fallback method for groups where direct computation fails
            return AutomorphismComputer._fallback_computation(group)

    @staticmethod
    def _fallback_computation(group):
        """Fallback method for automorphism group computation."""
        try:
            # Try using the automorphism group of the regular representation
            reg_rep = group.regular_representation()
            return reg_rep.automorphism_group()
        except Exception as e:
            raise RuntimeError(f"Could not compute automorphism group: {str(e)}")

    @staticmethod
    def to_permutation_group(aut_group):
        """Convert the automorphism group to permutation group representation."""
        try:
            return aut_group.permutation_group()
        except AttributeError:
            # If already a permutation group or conversion fails
            return aut_group

class OutputHandler:
    """Handles formatting and presentation of computation results."""

    @staticmethod
    def format_result(aut_group, detailed=False):
        """Format the automorphism group result for display."""
        result = {
            'group': aut_group,
            'order': aut_group.order(),
            'structure': str(aut_group.structure_description()),
            'is_abelian': aut_group.is_abelian(),
            'generators': list(aut_group.gens())
        }

        if detailed:
            result['conjugacy_classes'] = aut_group.conjugacy_classes()
            result['center'] = aut_group.center()
            result['derived_series'] = aut_group.derived_series()

        return result

    @staticmethod
    def print_result(result_dict, group_name="G"):
        """Print the formatted result in a readable way."""
        print(f"\nAutomorphism Group of {group_name}:")
        print(f"Order: {result_dict['order']}")
        print(f"Structure: {result_dict['structure']}")
        print(f"Is abelian: {'Yes' if result_dict['is_abelian'] else 'No'}")
        print("\nGenerators:")
        for i, gen in enumerate(result_dict['generators'], 1):
            print(f"  Generator {i}: {gen}")

        if 'conjugacy_classes' in result_dict:
            print(f"\nNumber of conjugacy classes: {len(result_dict['conjugacy_classes'])}")
        if 'center' in result_dict:
            print(f"Center order: {result_dict['center'].order()}")
        if 'derived_series' in result_dict:
            print("Derived series lengths:", [len(s) for s in result_dict['derived_series']])

def compute_and_display_automorphism_group(group, detailed=False):
    """
    Main function to compute and display the automorphism group of a given group.

    Args:
        group: A SageMath finite group
        detailed: Boolean for whether to show detailed information
    """
    try:
        # Validate and standardize input
        GroupInputHandler.validate_input(group)
        standardized_group = GroupInputHandler.standardize_representation(group)

        print(f"\nComputing automorphism group for group of order {standardized_group.order()}...")

        # Compute automorphism group
        aut_group = AutomorphismComputer.compute_automorphism_group(standardized_group)
        perm_aut_group = AutomorphismComputer.to_permutation_group(aut_group)

        # Format and display results
        result = OutputHandler.format_result(perm_aut_group, detailed)
        OutputHandler.print_result(result)

        return perm_aut_group

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return None

# Example usage and test cases
if __name__ == "__main__":
    print("SageMath Automorphism Group Computation Script")
    print("===============================================")

    # Example 1: Cyclic group
    print("\nExample 1: Cyclic group of order 5")
    C5 = CyclicPermutationGroup(5)
    compute_and_display_automorphism_group(C5)

    # Example 2: Symmetric group
    print("\nExample 2: Symmetric group S4")
    S4 = SymmetricGroup(4)
    compute_and_display_automorphism_group(S4)

    # Example 3: Dihedral group
    print("\nExample 3: Dihedral group D4")
    D4 = DihedralGroup(4)
    compute_and_display_automorphism_group(D4)

    # Example 4: Trivial group
    print("\nExample 4: Trivial group")
    trivial = PermutationGroup([])
    compute_and_display_automorphism_group(trivial)

    # Example 5: Direct product
    print("\nExample 5: Direct product C2 × C2")
    C2xC2 = AbelianGroup([2,2])
    compute_and_display_automorphism_group(C2xC2.permutation_group())

    # Example 6: Detailed output for S3
    print("\nExample 6: Detailed output for S3")
    S3 = SymmetricGroup(3)
    compute_and_display_automorphism_group(S3, detailed=True)