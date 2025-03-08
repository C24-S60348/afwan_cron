import os

tb_token = os.getenv("TB_TOKEN", "")
csftp_link = os.getenv("CSFTP_LINK" , "")
cronchecklink = os.getenv("CRON_CHECK_LINK", "")
fydevlink = os.getenv("FYDEV_LINK", "")
fy_code = os.getenv("FY_APP_CODE", "")
fy_app_staging = os.getenv("FY_APP_STAGING", "")
fy_app_prod = os.getenv("FY_APP_PROD", "")

username = os.getenv("FYDEV_USER", "")
password = os.getenv("FYDEV_PASS", "")


afwanemail = os.getenv("AFWAN_EMAIL", "")
