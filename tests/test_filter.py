import pytest

from smoof.filter import get_filter_query

@pytest.mark.parametrize(
    'click_infos, box_select_infos, var_nms, expected_output',
    [
        ([], [], [], None),
        ([None, None], [None, None], ['var_1', 'var_2'], None),
        (
            [
                {
                    'points': [
                        {
                            'curveNumber': 0,
                            'pointNumber': 0, 
                            'pointIndex': 0, 
                            'x': 0, 
                            'y': 0.6161616161616161,
                            'label': 0, 
                            'value': 0.6161616161616161
                        }
                    ]
                },
                None
            ],
            [None, None],
            ['var_1', 'var_2'],
            'var_1 == 0'
        ),
        (
            [None, None, None, None],
            [
                None,
                None,
                {
                    'points': 
                    [
                        {
                            'curveNumber': 0, 
                            'x': 19, 
                            'y': 0.07142857142857142, 
                            'binNumber': 9, 
                            'pointNumbers': [27, 38, 44, 49, 67, 136, 143, 144, 145, 175, 191, 192, 204, 226, 228, 238, 283, 291, 302, 311, 371, 372, 379, 385, 417, 424, 427, 505, 546, 566, 575, 585, 646, 651, 654, 675, 677, 687, 688, 700, 702, 715, 748, 757, 775, 786, 807, 834, 855, 877, 887]
                        }, 
                        {
                            'curveNumber': 0, 
                            'x': 21, 
                            'y': 0.056022408963585436, 
                            'binNumber': 10, 
                            'pointNumbers': [12, 37, 51, 56, 72, 91, 102, 106, 113, 115, 120, 131, 173, 227, 378, 391, 402, 404, 408, 421, 436, 441, 491, 494, 501, 622, 623, 624, 627, 640, 652, 664, 682, 725, 742, 762, 836, 840, 861, 876]
                        }
                    ], 
                    'range': {
                        'x': [15.234736842105262, 21.794736842105262], 
                        'y': [0.05307386112339673, 0.07459826035677429]
                    }
                },
                None
                ],
            ['var_1', 'var_2', 'var_3', 'var_4'],
            '(var_3 >= 15.23) & (var_3 <= 21.79)'
        ),
    ]
)
def test_get_filter_query(
    click_infos,
    box_select_infos,
    var_nms,
    expected_output
):

    obtained_output = get_filter_query(click_infos, box_select_infos, var_nms)

    assert expected_output == obtained_output
