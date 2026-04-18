#ifndef PTOLEMY2_H
#define PTOLEMY2_H

#include <QMainWindow>

QT_BEGIN_NAMESPACE
namespace Ui {
class Ptolemy2;
}
QT_END_NAMESPACE

class Ptolemy2 : public QMainWindow
{
    Q_OBJECT

public:
    Ptolemy2(QWidget *parent = nullptr);
    ~Ptolemy2();

private:
    Ui::Ptolemy2 *ui;
};
#endif // PTOLEMY2_H
