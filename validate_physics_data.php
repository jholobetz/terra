<?php
/**
 * Physics Data Validator (Legacy Bridge)
 * This script now calls the modern Python Integrity Shield.
 */

passthru("python3 integrity_shield.py", $return_var);
exit($return_var);
