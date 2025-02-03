# GIT

## Lister les commit : 
```bash
k@penguin:/tmp/Saur_fr_client main(1)* ± git log --pretty=oneline 
6d495601dc57856d709bb8eb47fe27687b400134 (HEAD -> main) mise à jour diverse / linting
a606bf1d9b5e06638a97307bd8f864122a282020 (tag: 0.1.4, origin/main, origin/HEAD) mise à jour diverse / linting
91a9aec997e274f50dbf4d1468120ecce65fb97e mise à jour diverse / linting
b6afa7fb5cb53f59d65a68c03bcd2b80deee6103 mise à jour diverse
0be2ec07978331a5d8a8e24f31e078016320c50d structuration
86fc36099ef93cbb314532f03c86df9608e6f672 Initial commit
```
## Attacher un tag :
```bash
k@penguin:/tmp/Saur_fr_client main(1)* 128 ± git tag -a 0.1.4 6d4956  -m 'ma version 0.1.4'
```

### ERREUR
```bash
k@penguin:/tmp/Saur_fr_client main(1)* 128 ± git tag -a 0.1.4 6d4956
fatal: tag '0.1.4' already exists
```
supprimer le tag
```bash
k@penguin:/tmp/Saur_fr_client main(1)* 129 ± git tag -d 0.1.4 
Deleted tag '0.1.4' (was 2a0cf03)
```

## Pousser un tag sur github
```bash
k@penguin:/tmp/Saur_fr_client main(1)* ± git push origin 0.1.4
Enumerating objects: 10, done.
Counting objects: 100% (10/10), done.
Delta compression using up to 4 threads
Compressing objects: 100% (6/6), done.
Writing objects: 100% (6/6), 730 bytes | 365.00 KiB/s, done.
Total 6 (delta 1), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (1/1), completed with 1 local object.
To github.com:cekage/Saur_fr_client.git
 * [new tag]         0.1.4 -> 0.1.4
```

# Pypi
## Build
```bash
k@penguin:/tmp/Saur_fr_client main(1)* 130 ± python3 -m build
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
(...)
adding 'saur_client-0.1.4.dist-info/RECORD'
removing build/bdist.linux-x86_64/wheel
Successfully built saur_client-0.1.4.tar.gz and saur_client-0.1.4-py3-none-any.whl
```
## Push (testpypi)
Le token est dans bitwarden
```bash
k@penguin:/tmp/Saur_fr_client main(1)* 130 ± twine upload --repository testpypi dist/* 
Uploading distributions to https://test.pypi.org/legacy/
Enter your API token: 
Uploading saur_client-0.1.4-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 17.5/17.5 kB • 00:00 • 11.3 MB/s
Uploading saur_client-0.1.4.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 17.2/17.2 kB • 00:00 • 9.1 MB/s

View at:
https://test.pypi.org/project/saur-client/0.1.4/
```