import base64
import json
import os
import shutil
from pathlib import Path
import re

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# The AES key used by Hollow Knight (32 bytes for AES-256)
AES_KEY = b'UKu52ePUBwetZ9wNX88o54dnfKRu0T1l'

# Static header and end byte found in Hollow Knight save files
C_SHARP_HEADER = bytes.fromhex('0001000000FFFFFFFF01000000000000000601000000')
END_HEADER_BYTE = bytes([11])

def decode_hollow_knight_save(file_path: Path) -> dict:
    """
    Decodes an encrypted Hollow Knight user.dat save file.

    Args:
        file_path: The path to the user.dat file (e.g., 'user1.dat').

    Returns:
        A dictionary representing the decrypted JSON content of the save file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file format is unexpected or decryption fails.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found at {file_path}")

    with open(file_path, 'rb') as f:
        encrypted_data = f.read()

    # 1. Verify and remove the C# header
    if not encrypted_data.startswith(C_SHARP_HEADER):
        raise ValueError("Invalid Hollow Knight save file header.")
    
    data_without_header = encrypted_data[len(C_SHARP_HEADER):]

    # 2. Remove the end header byte
    if not data_without_header.endswith(END_HEADER_BYTE):
        raise ValueError("Invalid Hollow Knight save file footer.")
    
    base64_encoded_content = data_without_header[:-len(END_HEADER_BYTE)]

    # 3. Base64 decode the content
    try:
        decoded_base64 = base64.b64decode(base64_encoded_content)
    except base64.binascii.Error as e:
        raise ValueError(f"Base64 decoding failed: {e}")

    # 4. Create AES cipher in ECB mode (no IV needed for ECB)
    cipher = AES.new(AES_KEY, AES.MODE_ECB)

    # 5. Decrypt the data
    try:
        decrypted_padded_data = cipher.decrypt(decoded_base64)
    except ValueError as e:
        raise ValueError(f"AES decryption failed (likely incorrect key or corrupted data): {e}")

    # 6. Unpad the decrypted data (PKCS#7 padding)
    try:
        unpadded_data = unpad(decrypted_padded_data, AES.block_size, style='pkcs7')
    except ValueError as e:
        raise ValueError(f"PKCS#7 unpadding failed (likely corrupted data or incorrect decryption): {e}")

    # 7. Decode to UTF-8 and parse as JSON
    try:
        json_string = unpadded_data.decode('utf-8')
        save_data = json.loads(json_string)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to decode to JSON: {e}")

    return save_data

def encode_hollow_knight_save(save_data: dict) -> bytes:
    """
    Encodes a modified Hollow Knight save data dictionary back into the encrypted format.

    Args:
        save_data: The dictionary representing the modified JSON content.

    Returns:
        Bytes representing the encrypted save file content.

    Raises:
        ValueError: If encoding or encryption fails.
    """
    # 1. Convert JSON to UTF-8 string
    json_string = json.dumps(save_data, separators=(',', ':')) # Use compact separators for smaller output
    json_bytes = json_string.encode('utf-8')

    # 2. Pad the data (PKCS#7 padding)
    try:
        padded_data = pad(json_bytes, AES.block_size, style='pkcs7')
    except ValueError as e:
        raise ValueError(f"PKCS#7 padding failed: {e}")

    # 3. Create AES cipher in ECB mode
    cipher = AES.new(AES_KEY, AES.MODE_ECB)

    # 4. Encrypt the data
    try:
        encrypted_data = cipher.encrypt(padded_data)
    except ValueError as e:
        raise ValueError(f"AES encryption failed: {e}")

    # 5. Base64 encode the content
    base64_encoded_content = base64.b64encode(encrypted_data)

    # 6. Prepend C# header and append end byte
    final_encrypted_data = C_SHARP_HEADER + base64_encoded_content + END_HEADER_BYTE

    return final_encrypted_data

# --- MODIFICATION FUNCTIONS ---

def maximize_health_and_soul(save_data: dict):
    """Maximizes player health, mask shards, soul, and soul vessels."""
    player_data = save_data.get('playerData', {})

    # Health
    player_data['health'] = 13
    player_data['maxHealth'] = 13
    player_data['maxHealthBase'] = 9  # Base for mask shards calculation
    player_data['heartPieces'] = 16 # 16 pieces for 4 masks (total 13 health)
    player_data['heartPieceCollected'] = True
    player_data['maxHealthCap'] = 13
    player_data['heartPieceMax'] = True
    player_data['CurrentMaxHealth'] = 13


    # Soul
    player_data['maxMP'] = 99
    player_data['MPCharge'] = 99
    player_data['MPReserve'] = 99
    player_data['MPReserveMax'] = 99
    player_data['vesselFragments'] = 9 # 9 fragments for 3 vessels
    player_data['vesselFragmentCollected'] = True
    player_data['MPReserveCap'] = 99
    player_data['vesselFragmentMax'] = True

    save_data['playerData'] = player_data
    print("Salud y Alma maximizadas.")

def give_max_geo(save_data: dict):
    """Sets player Geo to a very high value."""
    player_data = save_data.get('playerData', {})
    player_data['geo'] = 9999999
    save_data['playerData'] = player_data
    print("Geo al máximo.")

def unlock_all_charms(save_data: dict):
    """Unlocks all charms and makes fragile charms unbreakable."""
    player_data = save_data.get('playerData', {})

    # Charms
    player_data['charmSlots'] = 11 # Max notches
    player_data['charmsOwned'] = 40 # Total charms
    player_data['charmBenchMsg'] = True
    player_data['canOvercharm'] = True # Enable overcharming
    player_data['overcharmed'] = False # Start unovercharmed

    # Set all gotCharm_X to True
    for i in range(1, 41): # Charms are typically 1 to 40
        player_data[f'gotCharm_{i}'] = True
        player_data[f'newCharm_{i}'] = False # Mark as not new
        # Set all equipped charms to false to let player equip manually
        player_data[f'equippedCharm_{i}'] = False
    
    # Empty equipped charms list so player can choose
    player_data['equippedCharms'] = []

    # Make fragile charms unbreakable
    player_data['fragileHealth_unbreakable'] = True
    player_data['fragileGreed_unbreakable'] = True
    player_data['fragileStrength_unbreakable'] = True

    save_data['playerData'] = player_data
    print("Todos los amuletos desbloqueados y frágiles hechos irrompibles.")

def unlock_all_abilities(save_data: dict):
    """Unlocks all main player abilities."""
    player_data = save_data.get('playerData', {})

    # Movement abilities
    player_data['canDash'] = True
    player_data['hasDash'] = True
    player_data['canWallJump'] = True
    player_data['hasWalljump'] = True
    player_data['canSuperDash'] = True # Mothwing Cloak
    player_data['hasSuperDash'] = True
    player_data['canShadowDash'] = True # Shade Cloak
    player_data['hasShadowDash'] = True
    player_data['hasDoubleJump'] = True # Monarch Wings
    player_data['hasAcidArmour'] = True # Isma's Tear (acid immunity)

    # Other key abilities/items
    player_data['hasDreamNail'] = True
    player_data['dreamNailUpgraded'] = True
    player_data['hasDreamGate'] = True
    player_data['hasKingsBrand'] = True
    player_data['hasLantern'] = True # Lumafly Lantern
    player_data['hasQuill'] = True # Allows map drawing
    player_data['hasMap'] = True # Can view map
    player_data['mapAllRooms'] = True # Reveals all rooms on map

    # Spells and Nail Arts (ensure they are acquired)
    player_data['hasSpell'] = True
    player_data['hasNailArt'] = True
    player_data['hasCyclone'] = True
    player_data['hasDashSlash'] = True
    player_data['hasUpwardSlash'] = True
    player_data['hasAllNailArts'] = True

    save_data['playerData'] = player_data
    print("Todas las habilidades desbloqueadas.")

def upgrade_nail_and_spells(save_data: dict):
    """Upgrades nail damage and spell levels to maximum."""
    player_data = save_data.get('playerData', {})

    # Nail
    player_data['nailDamage'] = 4 # Pure Nail
    player_data['honedNail'] = True # Mark as honed
    player_data['nailSmithUpgrades'] = 4 # All upgrades purchased

    # Spells (level 0-2)
    player_data['fireballLevel'] = 2
    player_data['quakeLevel'] = 2
    player_data['screamLevel'] = 2

    save_data['playerData'] = player_data
    print("Clavo y hechizos mejorados al máximo.")

# --- MAIN SCRIPT LOGIC ---

def find_save_games_directory() -> Path | None:
    """Attempts to find the Hollow Knight save game directory based on the OS."""
    if os.name == 'nt':  # Windows
        save_path = Path(os.getenv('APPDATA')).parent / 'LocalLow' / 'Team Cherry' / 'Hollow Knight'
    elif os.name == 'posix':  # Linux or macOS
        if sys.platform == 'darwin':  # macOS
            save_path = Path('~/Library/Application Support/unity.Team Cherry.Hollow Knight').expanduser()
        else:  # Linux
            save_path = Path('~/.config/unity3d/Team Cherry/Hollow Knight').expanduser()
    else:
        return None

    if save_path.exists():
        return save_path
    return None

if __name__ == "__main__":
    import sys

    print("--- Hollow Knight Save Editor ---")
    print("Asegúrate de haber instalado 'pycryptodome': pip install pycryptodome")
    print("---------------------------------\n")

    save_dir = find_save_games_directory()
    selected_file_path = None

    if save_dir and save_dir.exists():
        print(f"Directorio de guardado encontrado: {save_dir}")
        save_files = sorted(list(save_dir.glob("user*.dat")))
        if save_files:
            print("Archivos de guardado disponibles:")
            for i, sf in enumerate(save_files):
                print(f"  {i+1}. {sf.name}")
            
            while True:
                choice = input(f"Selecciona un archivo para modificar (1-{len(save_files)}) o ingresa la ruta completa: ")
                if choice.isdigit() and 1 <= int(choice) <= len(save_files):
                    selected_file_path = save_files[int(choice) - 1]
                    break
                elif Path(choice).is_file() and Path(choice).suffix == '.dat':
                    selected_file_path = Path(choice)
                    break
                else:
                    print("Entrada inválida. Por favor, selecciona un número o ingresa una ruta de archivo válida.")
        else:
            print(f"No se encontraron archivos 'user*.dat' en {save_dir}.")
            file_input = input("Por favor, ingresa la ruta completa a tu archivo userX.dat: ")
            selected_file_path = Path(file_input)
    else:
        print("No se pudo encontrar el directorio de guardado de Hollow Knight automáticamente.")
        file_input = input("Por favor, ingresa la ruta completa a tu archivo userX.dat: ")
        selected_file_path = Path(file_input)

    if selected_file_path and selected_file_path.exists():
        print(f"\nProcesando archivo: {selected_file_path}")
        backup_path = selected_file_path.parent / f"{selected_file_path.name}.bak"
        print(f"Creando copia de seguridad en: {backup_path}")
        shutil.copy2(selected_file_path, backup_path)

        try:
            decoded_data = decode_hollow_knight_save(selected_file_path)
            
            print("\n--- Opciones de Modificación ---")
            print("1. Maximizar Salud y Alma")
            print("2. Geo al máximo")
            print("3. Desbloquear todos los Amuletos (y hacer frágiles irrompibles)")
            print("4. Desbloquear todas las Habilidades")
            print("5. Mejorar Clavo y Hechizos al máximo")
            print("6. Aplicar TODAS las modificaciones anteriores")
            print("0. Salir (No aplicar cambios)")

            mod_choice = input("Elige una opción: ")

            if mod_choice == '1':
                maximize_health_and_soul(decoded_data)
            elif mod_choice == '2':
                give_max_geo(decoded_data)
            elif mod_choice == '3':
                unlock_all_charms(decoded_data)
            elif mod_choice == '4':
                unlock_all_abilities(decoded_data)
            elif mod_choice == '5':
                upgrade_nail_and_spells(decoded_data)
            elif mod_choice == '6':
                maximize_health_and_soul(decoded_data)
                give_max_geo(decoded_data)
                unlock_all_charms(decoded_data)
                unlock_all_abilities(decoded_data)
                upgrade_nail_and_spells(decoded_data)
                print("\nTodas las modificaciones aplicadas.")
            elif mod_choice == '0':
                print("No se aplicaron cambios. El archivo original está intacto.")
                sys.exit()
            else:
                print("Opción inválida. No se aplicaron cambios.")
                sys.exit()
            
            # Save the modified data
            encoded_data = encode_hollow_knight_save(decoded_data)
            with open(selected_file_path, 'wb') as f:
                f.write(encoded_data)
            print(f"\n¡Archivo {selected_file_path.name} modificado y guardado con éxito!")
            print(f"Se ha guardado una copia de seguridad del archivo original en: {backup_path}")

        except FileNotFoundError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Error al procesar el archivo: {e}")
            print("Asegúrate de que sea un archivo de guardado válido de Hollow Knight.")
            print(f"El archivo original se ha restaurado desde la copia de seguridad: {backup_path}")
            shutil.copy2(backup_path, selected_file_path) # Attempt to restore original
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            print(f"El archivo original se ha restaurado desde la copia de seguridad: {backup_path}")
            shutil.copy2(backup_path, selected_file_path) # Attempt to restore original
    else:
        print("No se seleccionó o no se encontró un archivo válido. Saliendo.")
