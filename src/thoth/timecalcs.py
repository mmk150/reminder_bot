#Takes the amount (given by user) and the unit (given by word_to_time(message_fragment) and outputs seconds remaining until time.

def convert_timer(amount, units):
    assert type(units) == int
    assert type(amount) == float
    amount = float(amount)
    match units:
        case 1:
            return amount * 60
        case 2:
            return amount * 60 * 60
        case 3:
            return amount * 60 * 60 * 24
        case 4:
            return amount * 60 * 60 * 24 * 7


def word_to_time(word):
    unit = 0
    assert type(word) == str
    match word:
        case "minutes":
            print("minutes")
            unit = 1
        case "hours":
            print("hours")
            unit = 2
        case "days":
            print("days")
            unit = 3
        case "weeks":
            print("weeks")
            unit = 4
        case "months":
            print("months")
            unit = 5
        case "minute":
            print("minute")
            unit = 1
        case "hour":
            print("hour")
            unit = 2
        case "day":
            print("day")
            unit = 3
        case "week":
            print("week")
            unit = 4
        case "month":
            print("month")
            unit = 5
    return unit

