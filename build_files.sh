echo "BUILD START"

echo "Upgrading pip"
python3 -m pip install --upgrade pip

echo "Building the project..."
python3 -m pip install -r requirements.txt

echo "Make Migration..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

python3 manage.py collectstatic --noinput --clear
echo "BUILD END"