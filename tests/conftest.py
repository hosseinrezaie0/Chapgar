import os
import sys
from pathlib import Path
import pytest

# Ensure root directory is always on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

@pytest.fixture
def sample_persian_markup() -> str:
    return """= عنوان سند تستی
این یک پاراگراف ساده به زبان شیرین فارسی است.
نیم‌فاصله‌ها مانند «می‌رود» و «دانش‌آموزان» باید به درستی نمایش داده شوند.
"""

@pytest.fixture
def sample_bidi_markup() -> str:
    return """= تست جهت دوطرفه متن (BiDi)
متن فارسی به همراه کلمات انگلیسی مانند (Typst Engine) و کدهای `npm start` در این پاراگراف قرار دارند.
اعداد: 1403/05/20 و مقادیر درصدی: 99.5%
"""

@pytest.fixture
def sample_stress_markup() -> str:
    return """= گزارش تست تنش چاپگر
در این سند تمامی قابلیت‌های پیشرفته فارسی Typst بررسی می‌شود.

== ۱. لیست شماره‌دار و نشانه‌دار
- اولین آیتم با کلمه انگلیسی OpenSource
- دومین آیتم با عدد 12345
+ گام اول: بررسی فونت
+ گام دوم: تایید خروجی

== ۲. جدول اطلاعات
#table(
  columns: 3,
  fill: (x, y) => if y == 0 { luma(230) } else { none },
  [ردیف], [کالا], [قیمت (تومان)],
  [1], [لپ‌تاپ مدل Pro-X], [55,000,000],
  [2], [کیبورد مکانیکی RGB], [4,200,000]
)
"""
