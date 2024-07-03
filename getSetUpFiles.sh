wget http://10.42.0.1:8000/requirements.txt
wget http://10.42.0.1:8000/package-list.txt
wget http://10.42.0.1:8000/package-selections.txt

# Mettre à jour la liste des paquets
sudo apt update

# Installer dselect
sudo apt install dselect

# Lire les sélections de paquets
sudo dpkg --set-selections < package-selections.txt

# Installer les paquets sélectionnés via dselect
sudo dselect

# Installer les bibliothèques Python
pip install -r requirements.txt

# Installer les paquets npm locaux
npm install
