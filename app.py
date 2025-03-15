# pcsk_6FS7hW_7uFEW7rNsXq16NnEekCA2w122KDLL1zopDG3TyYqCtgeeT9NP9qH37Q6j3NChKJ

from flask import Flask, render_template, request, redirect, url_for, session

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set a secret key for session management


# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:353637@localhost/jobeasy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Seeker Table
class Seeker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Resume Table
class Resume(db.Model):
    resume_id = db.Column(db.Integer, primary_key=True)
    seeker_id = db.Column(db.Integer, db.ForeignKey('seeker.id'), nullable=False)  # Link to Seeker

    full_name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    education = db.Column(db.Text, nullable=False)  # Degree details
    technical_skills = db.Column(db.Text, nullable=False)
    work_experience = db.Column(db.Text)  # Job title and duration
    certifications = db.Column(db.Text)

# Company Table
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cin = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Job Listing Table
class JobListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)  # Add company_id column

    location = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    required_skills = db.Column(db.String(255), nullable=False)
    degrees = db.Column(db.String(100), nullable=False)
    experience_level = db.Column(db.String(50), nullable=False)
    job_description = db.Column(db.Text, nullable=False)

# Import the Pinecone library
from pinecone.grpc import PineconeGRPC as Pinecone

# Initialize a Pinecone client with your API key
pc = Pinecone(api_key="pcsk_6FS7hW_7uFEW7rNsXq16NnEekCA2w122KDLL1zopDG3TyYqCtgeeT9NP9qH37Q6j3NChKJ")

def pin_insert(job):
    print('job::', job)
    # Define the job data to be converted into embeddings
    data = [
        {
            "id": str(job.id),
            "text": f"{job.job_title} at {job.company_name} located in {job.location}. "
                    f"Job Type: {job.job_type}. Required Skills: {job.required_skills}. "
                    f"Degrees: {job.degrees}. Experience Level: {job.experience_level}. "
                    f"Description: {job.job_description}"
        }
    ]
    print('data::', data)

    # Convert the job text into numerical vectors that Pinecone can index
    embeddings = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[d['text'] for d in data],
        parameters={"input_type": "passage", "truncate": "END"}
    )

    # Target the index where you'll store the vector embeddings
    index = pc.Index("job-vector-store")

    # Prepare the records for upsert
    records = []
    for d, e in zip(data, embeddings):
        records.append({
            "id": d['id'],
            "values": e['values'],
            "metadata": {'text': d['text']}
        })

    # Upsert the records into the index
    index.upsert(
        vectors=records
    )


def pin_delete(job):
    pass

def pin_find_jobs(profile):
    pass


# Home Page - Choose Seeker or Company
@app.route('/')
def home():
    return render_template('home.html')

# Seeker Login Page
@app.route('/seeker_login', methods=['GET', 'POST'])
def seeker_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        seeker = Seeker.query.filter_by(email=email, password=password).first()
        if seeker:
            session['seeker_id'] = seeker.id  # Store the seeker ID in the session

            return redirect(url_for('seeker_dashboard'))  # Redirect to seeker dashboard after login
        else:
            return "Invalid credentials, try again."
    return render_template('seeker_login.html')

@app.route('/company_login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        cin = request.form['cin']
        password = request.form['password']
        company = Company.query.filter_by(cin=cin, password=password).first()
        if company:
            session['company_id'] = company.id  # Store the company ID in the session
        else:
            return "Invalid credentials, try again."  # Return error message if login fails


        if company:
            return redirect(url_for('company_dashboard'))  # Redirect to company dashboard after login
        else:
            return "Invalid credentials, try again."
    return render_template('company_login.html')

# Seeker Registration Page
@app.route('/seeker_register', methods=['GET', 'POST'])
def seeker_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        new_seeker = Seeker(name=name, email=email, password=password)
        db.session.add(new_seeker)
        db.session.commit()
        return redirect(url_for('seeker_login'))  # Redirect to login after registering
    return render_template('seeker_register.html')

@app.route('/company_register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        cin = request.form['cin']
        name = request.form['name']
        password = request.form['password']
        new_company = Company(cin=cin, name=name, password=password)
        db.session.add(new_company)
        db.session.commit()
        return redirect(url_for('company_login'))  # Redirect to login after registering
    return render_template('company_register.html')

@app.route('/seeker_dashboard')
def seeker_dashboard():
    return render_template('seeker_dashboard.html')

@app.route('/company_dashboard')
def company_dashboard():
    return render_template('company_dashboard.html')

# New Routes for Seekers
@app.route('/resume', methods=['GET', 'POST'])
def resume():
    seeker_id = session.get('seeker_id')  # Get the current seeker's ID from the session

    existing_resume = Resume.query.filter_by(seeker_id=seeker_id).first()
    
    if request.method == 'POST':
        if existing_resume:
            # Update existing resume
            existing_resume.full_name = request.form['full_name']
            existing_resume.phone_number = request.form['phone_number']
            existing_resume.email = request.form['email']
            existing_resume.education = request.form['education']
            existing_resume.technical_skills = request.form['technical_skills']
            existing_resume.work_experience = request.form['work_experience']
            existing_resume.certifications = request.form['certifications']
            db.session.commit()
        else:
            # Create new resume
            new_resume = Resume(seeker_id=seeker_id, full_name=request.form['full_name'],
                                 phone_number=request.form['phone_number'], 
                                 email=request.form['email'], 
                                 education=request.form['education'], 
                                 technical_skills=request.form['technical_skills'], 
                                 work_experience=request.form['work_experience'], 
                                 certifications=request.form['certifications'])
            db.session.add(new_resume)
            db.session.commit()
        return redirect(url_for('resume'))  # Redirect to the resume page after submission

    return render_template('resume.html', 
                           full_name=existing_resume.full_name if existing_resume else '', 
                           phone_number=existing_resume.phone_number if existing_resume else '', 
                           email=existing_resume.email if existing_resume else '', 
                           education=existing_resume.education if existing_resume else '', 
                           technical_skills=existing_resume.technical_skills if existing_resume else '', 
                           work_experience=existing_resume.work_experience if existing_resume else '', 
                           certifications=existing_resume.certifications if existing_resume else '')



    return render_template('resume.html', resume=existing_resume)

@app.route('/recommended_jobs')
def recommended_jobs():
    return render_template('recommended_jobs.html')

@app.route('/all_jobs')
def all_jobs():
    company_id = session.get('company_id')  # Get the current company's ID from the session
    job_listings = JobListing.query.filter_by(company_id=company_id).all()  # Query jobs for the logged-in company
    return render_template('all_jobs.html', job_listings=job_listings)  # Render the template with job listings

@app.route('/applications_sent')
def applications_sent():
    return render_template('applications_sent.html')

# New Routes for Companies
@app.route('/enlist_jobs', methods=['GET', 'POST'])
def enlist_jobs():
    if request.method == 'POST':
        job_title = request.form['job_title'] if 'job_title' in request.form else None

        company_name = request.form['company_name'] if 'company_name' in request.form else None

        location = request.form['location'] if 'location' in request.form else None

        job_type = request.form['job_type'] if 'job_type' in request.form else None

        required_skills = request.form['required_skills'] if 'required_skills' in request.form else None

        degrees = request.form['degrees'] if 'degrees' in request.form else None

        experience_level = request.form['experience_level'] if 'experience_level' in request.form else None

        job_description = request.form['job_description'] if 'job_description' in request.form else None


        # Save to database
        new_job = JobListing(job_title=job_title, company_name=company_name, company_id=session['company_id'], location=location,



                             job_type=job_type, required_skills=required_skills,
                             degrees=degrees, experience_level=experience_level,
                             job_description=job_description)
        db.session.add(new_job)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Rollback the session in case of error
            print(f"Error saving job listing: {e}")  # Log the error
            return "An error occurred while saving the job listing."
        
        pin_insert(new_job)
        return redirect(url_for('enlist_jobs'))  # Redirect to the job listing page after submission

    return render_template('enlist_jobs.html')

@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])


def edit_job(job_id):
    job = JobListing.query.get(job_id)  # Get the job listing by ID
    if request.method == 'POST':
        job.job_title = request.form['job_title']
        job.company_name = request.form['company_name']
        job.location = request.form['location']
        job.job_type = request.form['job_type']
        job.required_skills = request.form['required_skills']
        job.degrees = request.form['degrees']
        job.experience_level = request.form['experience_level']
        job.job_description = request.form['job_description']
        db.session.commit()  # Save changes to the database
        return redirect(url_for('all_jobs'))  # Redirect to all jobs page after editing
    return render_template('edit_job.html', job=job)  # Render edit form with job details

@app.route('/delete_job/<int:job_id>', methods=['POST'])  # New route for deleting job listings
def delete_job(job_id):
    job = JobListing.query.get(job_id)  # Get the job listing by ID
    if job:
        db.session.delete(job)  # Delete the job from the database
        db.session.commit()  # Commit the changes
    print(f"Delete request received for job ID: {job_id}")  # Debug statement
    return redirect(url_for('all_jobs'))  # Redirect to all jobs page after deletion





    company_id = session.get('company_id')  # Get the current company's ID from the session
    job_listings = JobListing.query.filter_by(company_id=company_id).all()  # Query jobs for the logged-in company
    return render_template('all_jobs.html', job_listings=job_listings)  # Render the template with job listings




@app.route('/applications_from_seekers')
def applications_from_seekers():
    return render_template('applications_from_seekers.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates the table if it doesn't exist
    app.run(debug=True)
