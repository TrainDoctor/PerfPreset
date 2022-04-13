cd "/home/deck/Downloads"
echo | pwd
# echo "curling"
curl -L https://files.pythonhosted.org/packages/ea/a3/3d3cbbb7150f90c4cf554048e1dceb7c6ab330e4b9138a40e130a4cc79e1/setuptools-62.1.0.tar.gz -o setuptools-62.1.0.tar.gz
curl -L https://files.pythonhosted.org/packages/44/7f/74192f47d67c8bf3c47bf0d8487b3457614c2c98d58b6617721d217f3f79/vdf-3.4.tar.gz -o vdf-3.4.tar.gz
tar -xf setuptools-62.1.0.tar.gz
tar -xf vdf-3.4.tar.gz
# echo "tarred"
cd setuptools-62.1.0
python setup.py install --user
cd ..
cd vdf-3.4
python setup.py install --user
exit