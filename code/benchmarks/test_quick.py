
PROBLEM_SET = [
    {"name": "berlin52", "optimal": 7542, "size": 52},
]

if __name__ == "__main__":
    import sys
    sys.path.insert(0, "..")
    from chapter4_validation import main
    sys.argv = ["test_quick.py", "--repetitions", "2"]
    main()
