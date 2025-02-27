from eslquickreads import app, bcrypt, db
from flask import render_template, url_for, flash, redirect
from flask_login import login_user, logout_user, login_required
from datetime import datetime
from eslquickreads.route.form.users_form import LoginForm, RegisterForm, EmailPasswordForm, PasswordForm
from eslquickreads.route.models.user_models import Users, Developer


@app.route("/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Normalize email to lowercase for case-insensitive matching
        normalized_email = form.email.data.lower() if form.email.data else None
        
        # First try to find by normalized email
        dev = Developer.query.filter_by(email=normalized_email).first()
        user = Users.query.filter_by(email=normalized_email).first()
        
        # If not found with normalized email, try with original email for legacy data
        if not (dev or user) and normalized_email != form.email.data:
            dev = Developer.query.filter_by(email=form.email.data).first()
            user = Users.query.filter_by(email=form.email.data).first()

        # If no match by email, we could be in transition to email_hash, so check that too
        # This will become primary method after full migration
        from eslquickreads.route.models.user_models import hash_email
        email_hash_value = hash_email(form.email.data)
        if not dev:
            dev = Developer.query.filter_by(email_hash=email_hash_value).first()
        if not user:
            user = Users.query.filter_by(email_hash=email_hash_value).first()

        # developer login
        if dev:
            if bcrypt.check_password_hash(dev.password, form.password.data):
                if dev.active:
                    # Update email_hash if not already populated
                    if not dev.email_hash:
                        dev.update_email_hash()
                        db.session.commit()
                    
                    login_user(dev)
                    return redirect(url_for('home'))
                else:
                    flash('Your account has been deactivated', 'info')
                    return redirect(url_for('login'))
            flash("Invalid Password", 'info')
            return redirect(url_for('login'))
        # user login
        elif user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                if user.active:
                    # Update email_hash if not already populated
                    if not user.email_hash:
                        user.update_email_hash()
                        db.session.commit()
                    
                    login_user(user)
                    return redirect(url_for('home'))
                else:
                    flash('Your account has been deactivated', 'info')
                    return redirect(url_for('login'))
            flash("Invalid Password", 'info')
            return redirect(url_for('login'))
        else:
            flash("Email not found", 'info')
            return redirect(url_for('login'))
    
    return render_template('login.html', form=form, title='Home')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Normalize email to lowercase
        normalized_email = form.email.data.lower() if form.email.data else None
        
        # Create new user with normalized email and hashed email
        user = Users(
            email=normalized_email, 
            password=hashed_password, 
            date_created=datetime.now()
        )
        
        # Set the email_hash value
        user.update_email_hash()
        
        # Uncomment for developer registration
        #user = Developer(email=form.email.data, password=hashed_password, date_created=datetime.now())
        #user.update_email_hash()
        
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form, title='Register')


@app.route("/send_reset_password", methods=['GET', 'POST'])
def send_reset_password():
    form = EmailPasswordForm()
    return render_template('login.html', form=form, title='Request Reset Password')


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    form = PasswordForm()
    return render_template('login.html', form=form, title='Reset Password')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html', title='Profile', Developer=Developer)
