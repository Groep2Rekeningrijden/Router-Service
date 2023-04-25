"""RouterService."""


class RouterService:
    """RouterService."""

    def __init__(self):
        """Initialize the RouterService."""
        pass

    def add(self, a, b):
        """
        Add two numbers.

        :param a: First number.
        :param b: Second number.
        :return: Sum of two numbers.
        :rtype: int
        """
        return a + b


def run():
    """Run the service."""
    service = RouterService()
    return service.add(1, 2)


if __name__ == "__main__":
    """
    Run the service.
    """
    run()
