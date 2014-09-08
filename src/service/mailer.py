from flask import render_template
import mandrill


from server_global import config


api = mandrill.Mandrill(config.MANDRILL_API_KEY)


def beta_registration(application_name, username, email):
    manager_url = '%s.manager.markuphive.com' % application_name
    app_url = '%s.app.markuphive.com' % application_name
    html = (
        '<p>'
            'Thank you for registering with Markup Hive.'
        '</p>'
        '<p>'
            'It is a web hosting platform that helps web '
            'developers skip the tedium of writing HTML, by using the '
            '<a href="http://www.learnjade.com">'
                'Jade templating language'
            '</a>.'
        '</p>'
        '<p>'
            'Your application name is %s. Your account manager back end '
            'login is available at <a href="%s">%s</a>. Your username is '
            '%s and you can use the password you provided during '
            'registration.'
        '</p>'
        '<p>'
            'You can view your uploaded application at '
            '<a href="%s">%s</a>.'
        '</p>'
        '<p>'
            'You can also reach support on the freenode IRC network in '
            'channel #markuphive'
        '</p>'
    )
    html_message = html % (
        application_name, manager_url, manager_url, username, app_url, 
        app_url
    )
    message = {
        'subject': "Welcome to Markuphive.com. Let's get you started",
        'from_email': 'notification@markuphive.com',
        'html': html_message,
        'to': [{'email': email}],
    }
    api.messages.send(message=message)


def password_reset(username, url, email):
    '''
    username - username account that is being reset
    url - password reset url
    email - email address to send to
    '''
    
    body = render_template('email/password-reset.jade', username=username, url=url)
    message = {
        'subject': "Markuphive.com password reset",
        'from_email': 'support@markuphive.com',
        'html': body,
        'to': [{'email': email}],
    }
    api.messages.send(message=message)
