@echo off
rem --- ���̉��̍s�̃p�X�������̊��ɍ��킹�ď��������Ă������� ---
cd /d "C:\Users\���ˎ��Ì����pPC\Documents\Python\phits-linac-validation"

echo --- PHITS���ʕ��z�]�������s���܂� ---
echo --- �[�x1.5cm�̔�r Z���v���t�@�C���̔�r ---
python src/Comp_measured_phits_v9.1.py deposit-y-water-15.out I150-1.5.csv --scale 1.00 --window 5 --order 2 --dd 2.0 --dta 2.0 --cutoff 10.0 --no-plot
echo --- �[�x5cm�̔�r Z���v���t�@�C���̔�r ---
python src/Comp_measured_phits_v9.1.py deposit-y-water-50.out I150-5.0.csv --scale 1.00 --window 5 --order 2 --dd 2.0 --dta 2.0 --cutoff 10.0 --no-plot
echo --- �[�x10cm�̔�r Z���v���t�@�C���̔�r ---
python src/Comp_measured_phits_v9.1.py deposit-y-water-100.out I150-10.0.csv --scale 1.00 --window 5 --order 2 --dd 2.0 --dta 2.0 --cutoff 10.0 --no-plot
echo --- �[�x20cm�̔�r Z���v���t�@�C���̔�r ---
python src/Comp_measured_phits_v9.1.py deposit-y-water-200.out I150-20.0.csv --scale 1.00 --window 5 --order 2 --dd 2.0 --dta 2.0 --cutoff 10.0 --no-plot
echo --- �[�x30cm�̔�r Z���v���t�@�C���̔�r ---
python src/Comp_measured_phits_v9.1.py deposit-y-water-300.out I150-30.0.csv --scale 1.00 --window 5 --order 2 --dd 2.0 --dta 2.0 --cutoff 10.0 --no-plot
echo --- �[�����ʕ��z(PDD)�̔�r ---
python src/Comp_measured_phits_v9.1.py deposit-z-water.out I600-PDD.csv --scale 1.00 --window 11 --order 7 --dd 2.0 --dta 2.0 --cutoff 10.0 --no-plot
echo --- �������������܂��� ---
pause