FROM python:3.9

RUN pip install 'simple-job-files>=0.1.1' waitress
ENV JOB_FILES_ROOT_DIRECTORY "/"
ENTRYPOINT ["waitress-serve", "--host=0.0.0.0", "--port=8000", "--expose-tracebacks", "--call", "simplejobfiles.app:JobFilesApp"]
