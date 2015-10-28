//#include <IMSCG_DefMeta2.hpp>

#define				READ_BUFFER_SIZE     512
#define             SEARCH_TYPE_ALL      0x01
#define             SEARCH_TYPE_MDN      0x02
#define     IPMD_TOTAL_LENGTH_LEN           4//addk


void ConvField( char *_buf, char * _data, int _len);
bool decoding(char *_fname);
bool MakeData(char * _fname, int _seq, char * _buf, int len);
void printHelpMessage();
void procOnlyMsg(char *inImsiFileName, int recordSeq, char *s, int isSearch, int isDetail, char *strSearch, int r);//addk
void GetFormatInfo(char * pstrFormatname, char * nstructCd, int isDetail );
void usage(char *s);


