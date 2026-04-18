proc disable {parent} {
    set widgets [info commands $parent*]
    foreach w $widgets {
        catch {$w configure -state disabled}
    }
}
proc enable {parent} {
    set widgets [info commands $parent*]
    foreach w $widgets {
        catch {$w configure -state normal}
    }
}
