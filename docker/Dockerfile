FROM python:3.9

RUN pip install simple-job-files
RUN pip install waitress
ENV JOB_FILES_ROOT_DIRECTORY "/"

# ENTRYPOINT ["python", "-c", "from simplejobfiles.app import JobFilesApp; wsgiapp = JobFilesApp('/'); from waitress import serve; serve(wsgiapp, listen='0.0.0.0:8080')"]
ENTRYPOINT ["waitress-serve", "--host=0.0.0.0", "--port=8000", "--expose-tracebacks", "--call", "simplejobfiles.app:JobFilesApp"]
