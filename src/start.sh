if [[ $TESTING -eq 1 ]]
then
    pytest test.py
else
    python main.py
fi
