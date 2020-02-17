import bisect

class SequencedList(list):
    """
    Sequenced list to maintain asks or bids.
    Each item of the list should be a tuple of `(price, quantity)`
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # For performance, just hardcode the logic to get the key
        self._key_list = [x[0] for x in self]

    def pop(self, index):
        self._key_list.pop(index)
        return super().pop(index)

    def append(self, subject):
        self._key_list.append(subject[0])
        return super().append(subject)

    def bisect(self, subject):
        key = subject[0]
        return bisect.bisect_left(self._key_list, key)

    # Add a new item into the list and maintain order
    def add(self, subject):
        key = subject[0]
        index = bisect.bisect_left(self._key_list, key)

        length = len(self)

        if index == length:
            self.append(subject)
            # insert_index, overridden
            return index, False

        origin = self[index]
        if origin[0] == key:
            quantity = subject[1]

            if quantity == 0:
                self.pop(index)
            else:
                self[index] = subject

            return index, True

        self.insert(index, subject)
        return index, False

    def insert(self, index, subject):
        self._key_list.insert(index, subject[0])
        return super().insert(index, subject)

    def __setitem__(self, index, subject):
        self._key_list[index] = subject[0]
        return super().__setitem__(index, subject)
