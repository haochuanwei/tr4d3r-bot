from datetime import datetime

with open('dummy_data/x.txt', 'w') as f:
    f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
