import platform
from fake_useragent import UserAgent

print(UserAgent(os=platform.system()).edge)
