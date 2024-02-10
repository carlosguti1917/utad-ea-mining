def check_nested_key_existence(dictionary, keys):
    try:
        # Iterate through each key in the list of keys
        for key in keys:
            # Access the value associated with the current key
            dictionary = dictionary[key]
        # If all keys are successfully accessed, return True
        return True
    except (KeyError, TypeError):
        # If any key is not found or if a non-dict type is encountered, return False
        return False


