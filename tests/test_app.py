from os import getcwd

from time import sleep

from dash.testing.application_runners import import_app

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


ID_PATH_TO_DF_FIELD = 'path_to_df'
ID_LOAD_DF_BUTTON = 'load_df_button'
ID_VAR_NMS_DROPDOWN = 'var_nms_dropdown'
CLASS_VAR_CHART = 'dash-graph'
CLASS_FILTER = 'filter'
CLASS_BTN_DROP_FILTER = 'drop_filter'

WORKING_DIR = getcwd()

def test_app(dash_duo):

    app = import_app('app')

    dash_duo.start_server(app)
    driver = dash_duo.driver

    path_to_df_input = WebDriverWait(driver, 5).until(
            lambda x: x.find_element(By.ID, ID_PATH_TO_DF_FIELD)
        )
    path_to_df_input.send_keys('{}/tests/test.csv'.format(WORKING_DIR))

    load_df_button = driver.find_element(By.ID, ID_LOAD_DF_BUTTON)
    load_df_button.click()

    try:
        var_nms_dropdown = WebDriverWait(driver, 5).until(
            lambda x: x.find_element(By.ID, ID_VAR_NMS_DROPDOWN)
        )
        assert True

    except TimeoutException:
        assert False

    var_select_actions = ActionChains(driver)
    for var_nm in ['Age', 'PClass']:
        var_select_actions.send_keys_to_element(var_nms_dropdown, var_nm)
        var_select_actions.send_keys_to_element(var_nms_dropdown, Keys.ENTER)

    var_select_actions.perform()
    sleep(2)

    try:
        var_charts = WebDriverWait(driver, 5).until(
            lambda x: x.find_elements(By.CLASS_NAME, CLASS_VAR_CHART)
        )
        assert len(var_charts) == 2

    except TimeoutException:
        assert False

    plot = var_charts[1].find_element(By.CLASS_NAME, 'plot')
    bar = plot.find_element(By.CLASS_NAME, 'point')
    
    click_select_actions_chain = ActionChains(driver)
    click_select_actions_chain.move_to_element(bar)
    click_select_actions_chain.click()
    click_select_actions_chain.perform()

    sleep(2)

    hist_bars = var_charts[0].find_elements(By.CLASS_NAME, 'point')
    box_select_btn = var_charts[0].find_elements(By.CLASS_NAME, 'modebar-btn')[3]
    box_select_btn = box_select_btn.find_element(By.TAG_NAME, 'svg')

    box_select_actions_chain = ActionChains(driver)
    box_select_actions_chain.move_to_element(var_charts[0])
    box_select_actions_chain.move_to_element(box_select_btn)
    box_select_actions_chain.click()
    box_select_actions_chain.move_to_element(hist_bars[0])
    box_select_actions_chain.click_and_hold()
    box_select_actions_chain.move_to_element(hist_bars[5])
    box_select_actions_chain.release()
    box_select_actions_chain.perform()

    sleep(2)

    try:
        filters = WebDriverWait(driver, 5).until(
            lambda x: x.find_elements(By.CLASS_NAME, CLASS_FILTER)
        )
        assert len(filters) == 2
    except TimeoutException:
        assert False
