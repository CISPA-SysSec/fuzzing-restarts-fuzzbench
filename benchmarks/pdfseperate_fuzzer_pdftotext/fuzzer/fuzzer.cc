#include "config.h"
#include <poppler-config.h>
#include <cstdio>
#include <cstdlib>
#include <cstddef>
#include <cstring>
#include "parseargs.h"
#include "printencodings.h"
#include "goo/GooString.h"
#include "goo/gmem.h"
#include "GlobalParams.h"
#include "Object.h"
#include "Stream.h"
#include "Array.h"
#include "Dict.h"
#include "XRef.h"
#include "Catalog.h"
#include "Page.h"
#include "PDFDoc.h"
#include "PDFDocFactory.h"
#include "TextOutputDev.h"
#include "CharTypes.h"
#include "UnicodeMap.h"
#include "PDFDocEncoding.h"
#include "Error.h"
#include <string>
#include <sstream>
#include <iomanip>
#include "Win32Console.h"
char path_in[64];
int fd_in;

int mymain()
{

    int firstPage = 1;
    int lastPage = 0;
    double resolution = 72.0;
    int x = 0;
    int y = 0;
    int w = 0;
    int h = 0;
    bool bboxLayout = false;
    bool physLayout = false;
    double fixedPitch = 0;
    bool rawOrder = false;
    bool discardDiag = false;
    bool htmlMeta = false;
    char textEncName[128] = "";
    bool noPageBreaks = false;
    PDFDoc *doc;
    GooString *fileName;
    GooString *textFileName;
    GooString *ownerPW, *userPW;
    TextOutputDev *textOut;
    Object info;
    bool ok;
    int exitCode;
    EndOfLineKind textEOL = TextOutputDev::defaultEndOfLine();
    exitCode = 99;

    fileName = new GooString(path_in);
    if (fileName->cmp("-") == 0)
    {
        delete fileName;
        fileName = new GooString("fd://0");
    }
    ownerPW = new GooString("owner");
    userPW = new GooString("user");

    puts(fileName->c_str());
    doc = PDFDocFactory().createPDFDoc(*fileName, ownerPW, userPW);

    if (!doc->isOk())
    {
        exitCode = 1;
        goto err2;
    }
    textFileName = fileName->copy();
    textFileName->append(htmlMeta ? ".html" : ".txt");
    if (lastPage < 1 || lastPage > doc->getNumPages())
    {
        lastPage = doc->getNumPages();
    }
    if (lastPage < firstPage)
    {
        error(errCommandLine, -1,
              "Wrong page range given: the first page ({0:d}) can not be after the last page ({1:d}).",
              firstPage, lastPage);
        goto err3;
    }
    textOut = new TextOutputDev(textFileName->c_str(),
                                physLayout, fixedPitch, rawOrder, htmlMeta, discardDiag);
    if (textOut->isOk())
    {
        textOut->setTextEOL(textEOL);
        if (noPageBreaks)
        {
            textOut->setTextPageBreaks(false);
        }
        if ((w == 0) && (h == 0) && (x == 0) && (y == 0))
        {
            doc->displayPages(textOut, firstPage, lastPage, resolution, resolution, 0,
                              true, false, false);
        }
        else
        {
            for (int page = firstPage; page <= lastPage; ++page)
            {
                doc->displayPageSlice(textOut, page, resolution, resolution, 0,
                                      true, false, false,
                                      x, y, w, h);
            }
        }
    }
    else
    {
        delete textOut;
        exitCode = 2;
        goto err3;
    }

    delete textOut;
    exitCode = 0;
    // clean up
err3:
    delete textFileName;
err2:
    delete doc;
    delete fileName;
err1:
err0:

    return exitCode;
}

extern "C" __attribute__((no_sanitize("undefined"))) int LLVMFuzzerInitialize(int *argc, char ***argv)
{
    strncpy(path_in, "/tmp/fuzz.input-XXXXXX", 31);
    fd_in = mkstemp(path_in);
    if (fd_in < 0)
    {
        printf("fd_in failed mkstemp, errno=%d\n", errno);
        return -2;
    }
    printf("mkstemp %s\n", path_in);
    globalParams = std::make_unique<GlobalParams>();
    globalParams->setErrQuiet(true);
    // poppler::set_debug_error_function(dummy_error_function, nullptr);
    return 0;
}

int writeFileIntoFD(int fd, const uint8_t *data, size_t size)
{
    lseek(fd, 0, SEEK_SET);
    if (size > 0 && write(fd, data, size) != size)
    {
        printf("failed write, errno=%d\n", errno);
        close(fd);
        return -3;
    }
    if (ftruncate(fd, size))
    {
        printf("failed truncate, errno=%d\n", errno);
        close(fd);
        return -3;
    }
    if (size > 0)
        lseek(fd, 0, SEEK_SET);
    return 0;
}

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{
    if (size < 1)
        return 0;
    int flag = writeFileIntoFD(fd_in, data, size);
    if (flag != 0)
    {
        return flag;
    }
    mymain();
    return 0;
}
