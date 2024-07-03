sudo apt-get update

nvm install 20

nvm install node

echo "install git"
sudo apt install git-all

echo "install mermaid"
npm install -g @mermaid-js/mermaid-cli

echo "installing python3"
sudo apt-get install python3

echo "installing python3-venv"
sudo apt-get install python3-venv

echo "installing chromium"
sudo apt-get 

echo "installing pip3"
sudo apt-get install python3-pip

echo "installing chrome"
sudo sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'
wget -O- https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo tee /etc/apt/trusted.gpg.d/linux_signing_key.pub
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 78BD65473CB3BD13
sudo apt-get update
sudo apt-get install google-chrome-stable

touch .env

echo "Step 1: Creating a virtual environment named 'venv'..."
python3 -m venv venv

echo "Step 2: Activating the virtual environment..."
source venv/bin/activate

echo "Step 3: Installing packages from requirements.txt..."
pip install -r requirements.txt

echo "Installed packages:"
pip list

echo "Setup complete. The virtual environment 'venv' is ready to use."

echo "Running gen_data.py"
python3 gen_data.py