numbers = [1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1]


def solution (nums, k):
    left=0
    right=-1
    zerocount=0
    maxim=0
    while left<len(nums):
        while right + 1<len(nums) and (zerocount<k or nums[right+1]==1):
            if nums[right+1]==0:
                zerocount+=1
            right+=1
        if right-left+1>maxim:
            maxim=right-left+1
        if nums[left]==0:
            zerocount-=1
        left+=1
    return maxim

print(solution(numbers, 2))
