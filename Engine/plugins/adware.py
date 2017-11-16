﻿# -*- coding:utf-8 -*-
# Author: Kei Choi(hanul93@gmail.com)


import os
import re
import kernel
import kavutil
import cryptolib


# -------------------------------------------------------------------------
# KavMain 클래스
# -------------------------------------------------------------------------
class KavMain:
    # ---------------------------------------------------------------------
    # init(self, plugins_path)
    # 플러그인 엔진을 초기화 한다.
    # 인력값 : plugins_path - 플러그인 엔진의 위치
    #         verbose      - 디버그 모드 (True or False)
    # 리턴값 : 0 - 성공, 0 이외의 값 - 실패
    # ---------------------------------------------------------------------
    def init(self, plugins_path, verbose=False):  # 플러그인 엔진 초기화
        self.verbose = verbose

        chars = r"A-Za-z0-9/\-=:.,_$%@'()[\]<> "
        shortest_run = 5

        regexp = '[%s]{%d,}' % (chars, shortest_run)
        self.p_string = re.compile(regexp)

        return 0  # 플러그인 엔진 초기화 성공

    # ---------------------------------------------------------------------
    # uninit(self)
    # 플러그인 엔진을 종료한다.
    # 리턴값 : 0 - 성공, 0 이외의 값 - 실패
    # ---------------------------------------------------------------------
    def uninit(self):  # 플러그인 엔진 종료
        return 0  # 플러그인 엔진 종료 성공

    # ---------------------------------------------------------------------
    # scan(self, filehandle, filename, fileformat)
    # 악성코드를 검사한다.
    # 입력값 : filehandle  - 파일 핸들
    #         filename    - 파일 이름
    #         fileformat  - 파일 포맷
    #         filename_ex - 파일 이름 (압축 내부 파일 이름)
    # 리턴값 : (악성코드 발견 여부, 악성코드 이름, 악성코드 ID) 등등
    # ---------------------------------------------------------------------
    def scan(self, filehandle, filename, fileformat, filename_ex):  # 악성코드 검사
        try:
            mm = filehandle

            # 미리 분석된 파일 포맷중에 PE 포맷이 있는가?
            if 'ff_pe' in fileformat:
                ff = fileformat['ff_pe']

                cert_off = ff['pe'].get('CERTIFICATE_Offset', 0)
                cert_size = ff['pe'].get('CERTIFICATE_Size', 0)
                
                if cert_off != 0 and cert_size != 0:
                    # 인증서 추출
                    cert_data = mm[cert_off:cert_off + cert_size]

                    if self.verbose:
                        print '-' * 79
                        kavutil.vprint('Engine')
                        kavutil.vprint(None, 'Engine', 'adware.kmd')

                    # String 추출
                    if len(cert_data):
                        if self.verbose:
                            print
                            kavutil.vprint('String')

                        for match in self.p_string.finditer(cert_data):
                            find_str = match.group()
                            find_str_off = match.start()

                            # 중요 문자열 시작전에 해당 문자열의 길이가 존재함
                            x = ord(cert_data[find_str_off-1])
                            if len(find_str) < x:
                                continue

                            buf = find_str[:x]
                            fsize = len(buf)

                            if self.verbose:
                                fmd5 = cryptolib.md5(buf)
                                kavutil.vprint(None, fmd5, '%3d : %s' % (fsize, buf))

                            if fsize and kavutil.handle_pattern_md5.match_size('adware', fsize):
                                fmd5 = cryptolib.md5(buf)
                                # print fsize, fmd5
                                vname = kavutil.handle_pattern_md5.scan('adware', fsize, fmd5)
                                if vname:
                                    return True, vname, 0, kernel.INFECTED
        except IOError:
            pass

        # 악성코드를 발견하지 못했음을 리턴한다.
        return False, '', -1, kernel.NOT_FOUND

    # ---------------------------------------------------------------------
    # disinfect(self, filename, malware_id)
    # 악성코드를 치료한다.
    # 입력값 : filename    - 파일 이름
    #        : malware_id - 치료할 악성코드 ID
    # 리턴값 : 악성코드 치료 여부
    # ---------------------------------------------------------------------
    def disinfect(self, filename, malware_id):  # 악성코드 치료
        try:
            # 악성코드 진단 결과에서 받은 ID 값이 0인가?
            if malware_id == 0:
                os.remove(filename)  # 파일 삭제
                return True  # 치료 완료 리턴
        except IOError:
            pass

        return False  # 치료 실패 리턴

    # ---------------------------------------------------------------------
    # listvirus(self)
    # 진단/치료 가능한 악성코드의 리스트를 알려준다.
    # 리턴값 : 악성코드 리스트
    # ---------------------------------------------------------------------
    def listvirus(self):  # 진단 가능한 악성코드 리스트
        vlist = list()  # 리스트형 변수 선언

        return vlist

    # ---------------------------------------------------------------------
    # getinfo(self)
    # 플러그인 엔진의 주요 정보를 알려준다. (제작자, 버전, ...)
    # 리턴값 : 플러그인 엔진 정보
    # ---------------------------------------------------------------------
    def getinfo(self):  # 플러그인 엔진의 주요 정보
        info = dict()  # 사전형 변수 선언

        info['author'] = 'Kei Choi'  # 제작자
        info['version'] = '1.0'      # 버전
        info['title'] = 'Adware Scan Engine'  # 엔진 설명
        info['kmd_name'] = 'adware'  # 엔진 파일 이름
        info['sig_num'] = kavutil.handle_pattern_md5.get_sig_num('adware')  # 진단/치료 가능한 악성코드 수

        return info