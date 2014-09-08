from boto.s3.connection import S3Connection

from application import config


s3c = S3Connection(
    config.AWS_ACCESS_KEY,
    config.AWS_SECRET_ACCESS_KEY
)

def upload_fields(filename, redirect=None):
    bucket = ''
    upload_key = 'upload/%s' % filename

    form_args = s3c.build_post_form_args(
        bucket,
        #success_action_redirect=redirect,
        key=upload_key,
        expires_in=60
    )
    return form_args
