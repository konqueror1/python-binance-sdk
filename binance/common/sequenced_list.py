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
        # suppose the list is [[1, 1], [2, 3]]

        key = subject[0]
        quantity = subject[1]

        index = bisect.bisect_left(self._key_list, key)

        length = len(self)

        if index == length:
            if quantity != 0:
                # add [3, 1], then
                # index -> 2, insert to the right
                self.append(subject)

            # else:
            # add [3, 0], but it has 0 quantity, so abandon it
            # > Receiving an event that removes a price level that is not
            # >   in your local order book can happen and is normal.

            # insert_index, overridden
            return index, False

        origin = self[index]
        if origin[0] == key:
            if quantity == 0:
                # add [2, 0]
                # we need to remove the second item, the list will be
                # [[1, 1]]
                self.pop(index)
            else:
                # add [2, 4], then the list will be
                # [[1, 1], [2, 4]]
                self[index] = subject

            return index, True

        if quantity != 0:
            # add [0.5, 10], then
            # index -> 0, insert to the left, the list will be
            # [[0.5, 10], [1, 1], [2, 3]]
            self.insert(index, subject)

        return index, False

    # Merge a list into the current one and maintain order
    def merge(self, l):
        for subject in l:
            self.add(subject)

    def insert(self, index, subject):
        self._key_list.insert(index, subject[0])
        return super().insert(index, subject)

    def __setitem__(self, index, subject):
        self._key_list[index] = subject[0]
        return super().__setitem__(index, subject)
