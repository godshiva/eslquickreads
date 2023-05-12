import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

st_time = time.time()


driver = webdriver.Chrome('./chromedriver.exe')

def gen_profile(element_type, elements):
    ret = []
    for element in elements:
        tag_name = element.tag_name
        text = element.text if element.text else ""
        typex = element.get_attribute('type')
        id = element.get_attribute('id')
        href = element.get_attribute('href')
        ret.append([tag_name, text, typex, id, href])
    return ret

def profile_page(url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    return gen_profile("buttons", driver.find_elements(by=By.CSS_SELECTOR, value="button")) + \
        gen_profile("links", driver.find_elements(by=By.CSS_SELECTOR, value="a")) + \
        gen_profile("input_boxes", driver.find_elements(by=By.CSS_SELECTOR, value="input"))

my_site = "https://www.eslquickreads.com/"
#my_site = "http://127.0.0.1:5000/"

# # todo: Forgot password submit page
# todo: have code submit page
# todo: register page
# todo: make cleanup utility, register with real user
# todo: watch lesson get marked as done

# main page

values = profile_page(my_site)
expected = [['button', 'Login', 'submit', '', None], ['a', 'Sign up', '', '', f'{my_site}register/'], ['a', 'Forgot Password', '', '', f'{my_site}forgotpassword/'], ['input', '', 'email', 'email', None], ['input', '', 'password', 'password', None]]
assert values == expected, (values, expected)

# forgot password page

values = profile_page(my_site + "forgotpassword/")
expected = [['input', '', 'hidden', 'csrf_token', None], ['input', '', 'text', 'email', None], ['input', '', 'submit', 'submit', None]]
assert values == expected, (values, expected)


# register page

values = profile_page(my_site + "register/")
expected = [['input', '', 'hidden', 'csrf_token', None], ['input', '', 'text', 'email', None], ['input', '', 'password', 'password', None], ['input', '', 'password', 'confirm_password', None], ['input', '', 'submit', 'submit', None]]
assert values == expected, (values, expected)


values = profile_page(my_site + "havecode/")
expected = [['input', '', 'hidden', 'csrf_token', None], ['input', '', 'text', 'email', None], ['input', '', 'text', 'verification_code', None], ['input', '', 'password', 'password', None], ['input', '', 'password', 'confirm_password', None], ['input', '', 'submit', 'submit', None]]
assert values == expected, (values, expected)


# TODO: Have this be a dynamically created user
my_user = "a@x"
my_pass = "n94t_7fb?*iNS):"

driver.get(my_site)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

email_input = driver.find_element(By.ID, 'email')
email_input.send_keys(my_user)

# Find the password input field and fill in the password
password_input = driver.find_element(By.ID, 'password')
password_input.send_keys(my_pass)

# Find the login button and click it
login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
login_button.click()

# Wait for the new page to load (you can modify the expected condition as needed)
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.ID, 'logout-link')))
values = profile_page(my_site + "home")  # todo: make route tolerant of "/home/"
expected = [['a', 'Logout', '', 'logout-link', f'{my_site}logout'], ['a', 'Lesson 1', '', '', f'{my_site}lesson/1']]
assert values == expected, (values, expected)

driver.quit()

en_time = time.time()

print(f"Elapsed time: {en_time-st_time}")