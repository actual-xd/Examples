nums = [1,0,1,0,1,0,1,1]



def longest_one_with_flips(nums, k):
    l = 0
    r = -1
    result = 0
    zeros_count = 0


    while l < len(nums):
        while r + 1 < len(nums) and (nums[r + 1] == 1 or zeros_count < k):
            if nums[r + 1] == 0:
                zeros_count += 1
            r += 1
        result = max(result, r - l + 1)
        if nums[l] == 0:
            zeros_count -= 1
        l += 1
    return result

print(longest_one_with_flips(nums, 2))
