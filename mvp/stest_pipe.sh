#!/bin/bash

spark-submit --master spark://ip-10-0-0-6:7077 --executor-memory 1G --driver-memory 6G test_pipe.py 
