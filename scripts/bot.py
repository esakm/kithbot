import json, bs4, time
from selenium import webdriver

targets = []
driver: webdriver.Chrome

search_url = "https://kith.com/pages/search-results-page?q={}"
cart_url = "https://kith.com/cart"
# Check out button
# button type="submit" name="checkout" class="btn"
char_encodings = {
    "/": "%2F",
    "\\": "%5C",
    ";": "%3B",
    "'": "%27",
    "[": "%5B",
    "]": "%5D",
    ",": "%2C",
    "=": "%3D",
    " ": "+"
}


def get_config_file():
    with open('data\\config.json') as fd:
        return json.load(fd)


def get_targets(config_data):
    global targets
    for target in config_data["targets"]:
        targets.append(target)


def launch_browser():
    global driver
    driver = webdriver.Chrome()


def change_size(size, back_up_size=None):
    try:
        driver.find_element_by_class_name("dk-select").click()
        options = driver.find_element_by_class_name("dk-select-options").find_elements_by_class_name("dk-option")
        for option in options:
            if option.text == str(size):
                option.click()
                return True
        for option in options:
            if isinstance(back_up_size, list):
                if option.text in back_up_size:
                    option.click()
                    return True
            elif isinstance(back_up_size, str):
                if option.text == back_up_size:
                    option.click()
                    return True
        return False
    except Exception as e:
        print(e.args)


def replace_special_chars(item_name):
    global char_encodings
    for char, replacement in char_encodings.items():
        if char in item_name:
            item_name = item_name.replace(char, replacement)
    return item_name


def prepare_for_query(item_name):
    item_name = replace_special_chars(item_name)
    item_name = "-".join(item_name.rsplit())
    return item_name


def get_search_query_url(item):
    global search_url
    name = item["name"].lower()
    name = prepare_for_query(name)
    return search_url.format(name)


def go_to_item_page(item_name):
    item_name = item_name.lower()
    for product in driver.find_element_by_class_name("snize-search-results-main-content").find_elements_by_class_name("snize-product"):
        if item_name in product.text.lower():
            try:
                product.click()
                return True
            except Exception:
                return False


def go_to_next_page(page_number):
    try:
        driver.find_element_by_link_text(str(page_number)).click()
    except Exception:
        pass

def add_to_cart():
    try:
        driver.find_element_by_class_name("product-single-add-to-cart").click()
    except Exception:
        pass

def go_to_cart():
    global cart_url
    driver.get(cart_url)


def go_to_checkout():
    driver.find_element_by_name("checkout").click()


def main():
    config = get_config_file()
    get_targets(config)
    launch_browser()
    driver.get("https://kith.com")
    driver.add_cookie({"name": "KL_FORMS_MODAL", "value": "{%22disabledForms%22:{%22KyEV5m%22:{%22lastCloseTime%22:1540"
                                                          "526200%2C%22successActionTypes%22:[]}}}", "domain": "kith.com"})
    for target in targets:
        target_name = target['name']
        driver.get(get_search_query_url(target))
        for i in range(1, 6):
            if go_to_item_page(target_name):
                change_size(target['size'])
                time.sleep(1)
                add_to_cart()
                break
            else:
                go_to_next_page(i + 1)
    go_to_cart()
    go_to_checkout()
    time.sleep(500)

main()