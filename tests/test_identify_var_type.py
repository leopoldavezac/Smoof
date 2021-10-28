import pytest

from pandas import Series

from smoof.identify_var_type import VarTypeIdentifier


@pytest.mark.parametrize(
    'input_val, expected_output_val',
    [
        (Series([i for i in range(100)]), 'numeric'),
        (Series([i/2 for i in range(100)]), 'numeric'),
        (Series([1 for _ in range(100)]), 'category_short'),
        (Series(['label' for _ in range(100)]), 'category_short'),
        (Series(['label_%d'%i for i in range(100)]), 'category_long'),
        (Series(['10/12/2021' for _ in range(100)]), 'date'),
    ]
)
def test_VarTypeIdentifier_identify_type(input_val, expected_output_val):

    var_type_identifier = VarTypeIdentifier(input_val)
    var_type_identifier.identify_type()

    assert expected_output_val == var_type_identifier.get_type()
