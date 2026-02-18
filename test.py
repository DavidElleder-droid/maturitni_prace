# ...existing code...
def bubble_sort(arr):
    """Jednoduchý in-place bubble sort. Vrací seřazený seznam (stále ten samý objekt)."""
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

if __name__ == "__main__":
    data = [64, 34, 25, 12, 22, 11, 90]
    print("Před:", data)
    print("Po:", bubble_sort(data))