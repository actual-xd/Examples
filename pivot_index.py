nums = [7, -1, 4, 10, 5, 5]


def pivot_index(nums):
    total_sum = sum(nums)
    prefix_sum = 0
    for i in range(len(nums)):
        if prefix_sum == total_sum - prefix_sum - nums[i]:
            return i
        prefix_sum += nums[i]
    return -1


print(pivot_index(nums))

# найти индекс элемента, слева и справа от которого сумма элементов массива одинаковая.
