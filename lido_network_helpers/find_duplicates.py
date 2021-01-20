def spot_duplicates(operators, key, original_op=None):
    """Compare every available key with other keys to spot duplicates"""

    duplicates_found = []
    for operator in operators:
        for second_key in operator["keys"]:
            if key["key"] == second_key["key"]:
                if not original_op:
                    duplicates_found.append({"op": operator, "key": second_key})
                elif (original_op["id"], key["index"]) != (
                    operator["id"],
                    second_key["index"],
                ):
                    duplicates_found.append({"op": operator, "key": second_key})
    return duplicates_found


def find_duplicates(operators):
    """Loop through all keys and add information about duplicates"""

    for op_i, op in enumerate(operators):
        for key_i, key in enumerate(op["keys"]):

            operators[op_i]["keys"][key_i]["duplicate"] = False
            op["keys"][key_i]["duplicates"] = []

            duplicates = spot_duplicates(operators, key, op)

            for duplicate_i, duplicate in enumerate(duplicates):
                operators[op_i]["keys"][key_i]["duplicates"].append(
                    dict(
                        op_id=duplicate["op"]["id"],
                        op_name=duplicate["op"]["name"],
                        index=duplicate["key"]["index"],
                        approved=bool(duplicate["op"]["stakingLimit"]),
                        used=duplicate["key"]["used"],
                    )
                )

            if duplicates:
                operators[op_i]["keys"][key_i]["duplicate"] = True

    return operators
